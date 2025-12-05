import configparser
from pathlib import Path

from PySide6.QtCore import QRect, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matecon.material import Material
from matecon.spreadsheet_reader import READABLE_EXTS
from matecon.utils import write_txt

# デフォルトラベル
DEFAULT_LABEL_TEXT = "Excelファイルを選択してください\n(またはこのウィンドウにファイルをドロップ)"

# 設定ファイル
INI_FILE = Path.cwd() / "matecon.ini"
INI_FILE_ENCODING = "shift-jis"

# デフォルトウィンドウ (x, y, width, height)
DEFAULT_WINDOW_GEOMETRY = QRect(100, 100, 360, 180)


class ConfigManager:
    """GUI 設定を管理するクラス"""

    def __init__(self, ini_file: Path = INI_FILE):
        self.ini_file = ini_file
        self.config = configparser.ConfigParser()
        self._load()

    def _load(self):
        """設定ファイルを読み込む"""
        if self.ini_file.exists():
            self.config.read(self.ini_file, encoding=INI_FILE_ENCODING)

    def save(self):
        """設定ファイルに保存"""
        self.ini_file.parent.mkdir(parents=True, exist_ok=True)
        with self.ini_file.open("w", encoding=INI_FILE_ENCODING) as f:
            self.config.write(f)

    def get_window_geometry(self) -> QRect:
        """ウィンドウのジオメトリ (x, y, width, height) を取得"""
        if not self.config.has_section("window"):
            return DEFAULT_WINDOW_GEOMETRY
        return QRect(
            self.config.getint("window", "x", fallback=DEFAULT_WINDOW_GEOMETRY.x()),
            self.config.getint("window", "y", fallback=DEFAULT_WINDOW_GEOMETRY.y()),
            self.config.getint("window", "width", fallback=DEFAULT_WINDOW_GEOMETRY.width()),
            self.config.getint("window", "height", fallback=DEFAULT_WINDOW_GEOMETRY.height()),
        )

    def set_window_geometry(self, geometry: QRect):
        """ウィンドウのジオメトリ (x, y, width, height) を保存"""
        if not self.config.has_section("window"):
            self.config.add_section("window")
        self.config.set("window", "x", str(geometry.x()))
        self.config.set("window", "y", str(geometry.y()))
        self.config.set("window", "width", str(geometry.width()))
        self.config.set("window", "height", str(geometry.height()))

    def get_last_directory(self) -> str:
        """最後に開いたディレクトリを取得"""
        if not self.config.has_section("paths"):
            return str(Path.home())
        return self.config.get("paths", "last_directory", fallback=str(Path.home()))

    def set_last_directory(self, directory: str):
        """最後に開いたディレクトリを保存"""
        if not self.config.has_section("paths"):
            self.config.add_section("paths")
        self.config.set("paths", "last_directory", directory)


class MaterialWorker(QThread):
    """Material 処理をバックグラウンドで実行"""

    finished = Signal(str)  # 成功時
    error = Signal(str)  # エラー時

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            mate = Material(self.file_path)
            txt_path = write_txt(self.file_path, mate.format_lines)
            for book in mate.table.books:
                book.close()
            self.finished.emit(str(txt_path))
        except FileNotFoundError as e:
            self.error.emit(f"ファイルが見つかりません: {e}")
        except ValueError as e:
            self.error.emit(f"ファイル形式エラー: {e}")
        except Exception as e:
            self.error.emit(f"予期しないエラー: {type(e).__name__}: {e}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()

        self.setWindowTitle("まてコン")

        # 保存されたウィンドウ設定を復元
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(geometry)

        self.v_layout = QVBoxLayout()

        self.label = QLabel(DEFAULT_LABEL_TEXT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.button_select = QPushButton("ファイル選択")
        self.button_select.clicked.connect(self.select_file)
        self.button_convert = QPushButton("変換")
        self.button_convert.clicked.connect(self.convert_file)
        self.button_convert.setEnabled(False)

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.button_select)
        self.v_layout.addWidget(self.button_convert)
        self.setLayout(self.v_layout)

        self.setAcceptDrops(True)  # ドロップ受付を有効化
        self.worker: MaterialWorker | None = None
        self.selected_file_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_ext = Path(url.toLocalFile()).suffix.lower()
                if file_ext in READABLE_EXTS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in READABLE_EXTS:
                continue
            self.selected_file_path = file_path
            self.label.setText(f"ファイル: {Path(file_path).name}\n「変換」ボタンを押してください")
            self.button_convert.setEnabled(True)
            return

    def select_file(self):
        filter_str = "Excel Files (*.xlsx *.xlsm)"
        last_dir = self.config_manager.get_last_directory()
        file_path, _ = QFileDialog.getOpenFileName(self, "Excelファイルを選択", last_dir, filter_str)
        if not file_path:
            return
        # ディレクトリを保存
        parent_dir = str(Path(file_path).parent)
        self.config_manager.set_last_directory(parent_dir)
        self.config_manager.save()
        self.selected_file_path = file_path
        self.label.setText(f"ファイル: {Path(file_path).name}\n「変換」ボタンを押してください")
        self.button_convert.setEnabled(True)

    def convert_file(self):
        if not self.selected_file_path:
            return
        self.handle_file(self.selected_file_path)

    def handle_file(self, file_path: str):
        self.button_select.setEnabled(False)
        self.button_convert.setEnabled(False)
        self.label.setText("処理中...")

        self.worker = MaterialWorker(file_path)
        self.worker.finished.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_success(self, txt_path: str):
        self.button_select.setEnabled(True)
        self.button_convert.setEnabled(True)
        self.label.setText(DEFAULT_LABEL_TEXT)
        self.selected_file_path = None
        QMessageBox.information(self, "完了", f"{txt_path}\nテキストデータを出力しました。")

    def _on_error(self, error_msg: str):
        self.button_select.setEnabled(True)
        self.button_convert.setEnabled(True)
        if self.selected_file_path:
            file_name = Path(self.selected_file_path).name
            self.label.setText(f"ファイル: {file_name}\n「変換」ボタンを押してください")
        else:
            self.label.setText(DEFAULT_LABEL_TEXT)
        QMessageBox.critical(self, "エラー", error_msg)

    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        geometry = QRect(self.x(), self.y(), self.width(), self.height())
        self.config_manager.set_window_geometry(geometry)
        self.config_manager.save()
        event.accept()
