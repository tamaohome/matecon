from __future__ import annotations

import configparser
from dataclasses import dataclass
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
from matecon.spreadsheet_reader import validate_excel_filepath
from matecon.utils import write_txt

# デフォルトラベル
DEFAULT_LABEL_TEXT = "Excelファイルを選択してください\n(またはこのウィンドウにファイルをドロップ)"

# 設定ファイル
INI_FILE = Path.cwd() / "matecon.ini"
INI_FILE_ENCODING = "shift-jis"


@dataclass
class WindowGeometry:
    """ウィンドウ位置およびサイズを保持するクラス"""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        """x, y の範囲を制限"""
        self.x = max(0, self.x)
        self.y = max(0, self.y)

    @staticmethod
    def default() -> WindowGeometry:
        """デフォルト値を返す"""
        return WindowGeometry(100, 100, 360, 180)

    @staticmethod
    def from_qwidget(qwidget: QWidget) -> WindowGeometry:
        """`QWidget` インスタンスより `WindowGeometry` を取得する"""
        g = qwidget.geometry()
        return WindowGeometry(g.x(), g.y(), g.width(), g.height())

    def to_qrect(self) -> QRect:
        """`QRect` 型に変換する"""
        return QRect(self.x, self.y, self.width, self.height)


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

    def get_window_geometry(self) -> WindowGeometry:
        """ウィンドウのジオメトリ (x, y, width, height) を取得"""
        if not self.config.has_section("window"):
            return WindowGeometry.default()
        x = self.config.getint("window", "x", fallback=WindowGeometry.default().x)
        y = self.config.getint("window", "y", fallback=WindowGeometry.default().y)
        width = self.config.getint("window", "width", fallback=WindowGeometry.default().width)
        height = self.config.getint("window", "height", fallback=WindowGeometry.default().height)
        return WindowGeometry(x, y, width, height)

    def set_window_geometry(self, geometry: WindowGeometry):
        """ウィンドウのジオメトリ (x, y, width, height) を保存"""
        if not self.config.has_section("window"):
            self.config.add_section("window")
        self.config.set("window", "x", str(geometry.x))
        self.config.set("window", "y", str(geometry.y))
        self.config.set("window", "width", str(geometry.width))
        self.config.set("window", "height", str(geometry.height))

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
            try:
                txt_path = write_txt(self.file_path, mate.format_lines)
                self.finished.emit(str(txt_path))
            finally:
                # リソースを解放
                for book in mate.table.books:
                    book.close()
        except Exception as e:
            self.error.emit(f"予期しないエラー:\n{type(e).__name__}: {e}")


class MainWindow(QWidget):
    @staticmethod
    def _is_valid_excel_file(file_path: str) -> bool:
        """Excelファイルの妥当性を検証"""
        try:
            validate_excel_filepath(file_path)
            return True
        except (FileNotFoundError, ValueError, OSError):
            return False

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()

        self.setWindowTitle("まてコン")

        # 保存されたウィンドウ設定を復元
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(geometry.to_qrect())

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
        if event.mimeData().hasUrls() and any(
            self._is_valid_excel_file(url.toLocalFile()) for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not self._is_valid_excel_file(file_path):
                continue
            self._set_selected_file(file_path)
            return

    def _set_selected_file(self, file_path: str) -> None:
        """ファイル選択時の共通UI更新処理"""
        self.selected_file_path = file_path
        file_name = Path(file_path).name
        self.label.setText(f"ファイル: {file_name}\n「変換」ボタンを押してください")
        self.button_convert.setEnabled(True)

    def _reset_ui(self) -> None:
        """UIを初期状態にリセット"""
        self.label.setText(DEFAULT_LABEL_TEXT)
        self.selected_file_path = None
        self.button_convert.setEnabled(False)

    def _set_processing_state(self, is_processing: bool) -> None:
        """処理中/待機中の状態を設定"""
        self.button_select.setEnabled(not is_processing)
        self.button_convert.setEnabled(not is_processing and self.selected_file_path is not None)
        if is_processing:
            self.label.setText("処理中...")

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
        self._set_selected_file(file_path)

    def convert_file(self):
        if not self.selected_file_path:
            return
        self.handle_file(self.selected_file_path)

    def handle_file(self, file_path: str):
        """
        入力ファイルに対する `Material` 処理をバックグラウンドで実行する

        - 既存の `MaterialWorker` が実行中の場合は終了を待つ
        - 処理完了後は自動的に `MaterialWorker` インスタンスをメモリから解放する
        """
        # 既存の MaterialWorker があれば終了を待つ
        if self.worker is not None:
            # MaterialWorker の実行状態を確認
            try:
                if self.worker.isRunning():
                    self.worker.quit()
                    self.worker.wait()
            except RuntimeError:
                # MaterialWorker が削除済みの場合はスキップ
                pass

        self._set_processing_state(True)

        self.worker = MaterialWorker(file_path)
        self.worker.finished.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self.worker.deleteLater)  # メモリ解放
        self.worker.error.connect(self.worker.deleteLater)
        self.worker.start()

    def _on_success(self, txt_path: str):
        self._set_processing_state(False)
        self._reset_ui()
        QMessageBox.information(self, "完了", f"{txt_path}\nテキストデータを出力しました。")

    def _on_error(self, error_msg: str):
        self._set_processing_state(False)
        if self.selected_file_path:
            file_name = Path(self.selected_file_path).name
            self.label.setText(f"ファイル: {file_name}\n「変換」ボタンを押してください")
            self.button_convert.setEnabled(True)
        else:
            self._reset_ui()
        QMessageBox.critical(self, "エラー", error_msg)

    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        geometry = WindowGeometry.from_qwidget(self)
        self.config_manager.set_window_geometry(geometry)
        self.config_manager.save()
        event.accept()
