from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
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
        self.setWindowTitle("まてコン")
        self.resize(240, 120)
        self.v_layout = QVBoxLayout()

        self.label = QLabel(DEFAULT_LABEL_TEXT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.button = QPushButton("ファイル選択")
        self.button.clicked.connect(self.select_file)

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.button)
        self.setLayout(self.v_layout)

        self.setAcceptDrops(True)  # ドロップ受付を有効化
        self.worker = None

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
            if file_ext in READABLE_EXTS:
                self.handle_file(file_path)
                return

    def select_file(self):
        filter_str = "Excel Files (*.xlsx *.xlsm)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Excelファイルを選択", "", filter_str)
        if file_path:
            self.handle_file(file_path)

    def handle_file(self, file_path: str):
        self.button.setEnabled(False)
        self.label.setText("処理中...")

        self.worker = MaterialWorker(file_path)
        self.worker.finished.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_success(self, txt_path: str):
        self.button.setEnabled(True)
        self.label.setText(DEFAULT_LABEL_TEXT)
        QMessageBox.information(self, "完了", f"{txt_path}\nテキストデータを出力しました。")

    def _on_error(self, error_msg: str):
        self.button.setEnabled(True)
        self.label.setText(DEFAULT_LABEL_TEXT)
        QMessageBox.critical(self, "エラー", error_msg)
