from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matecon.material import Material
from matecon.utils import write_txt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("まてコン")
        self.resize(240, 120)
        self.v_layout = QVBoxLayout()

        self.label = QLabel("xlsxファイルを選択してください\n(またはこのウィンドウにファイルをドロップ)")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.button = QPushButton("ファイル選択")
        self.button.clicked.connect(self.select_file)

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.button)
        self.setLayout(self.v_layout)

        self.setAcceptDrops(True)  # ドロップ受付を有効化

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
        file_path, _ = QFileDialog.getOpenFileName(self, "xlsxファイルを選択", "", filter_str)
        if file_path:
            self.handle_file(file_path)

    def handle_file(self, file_path):
        try:
            mate = Material(file_path)
            txt_path = write_txt(file_path, mate.format_lines)
            QMessageBox.information(self, "完了", f"{txt_path}\nテキストデータを出力しました。")
        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))
