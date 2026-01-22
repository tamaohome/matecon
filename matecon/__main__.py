import sys
import warnings

from PySide6.QtWidgets import QApplication

from matecon.gui.view import MainWindow
from matecon.io.io import get_filepaths_from_args

# openpyxl の警告を無視
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def app():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    allow_exts = [".xlsx", ".xlsm"]
    # コマンドライン引数からファイルパスを取得
    initial_filepaths = get_filepaths_from_args(allow_exts, sys.argv[1:])

    window = MainWindow(initial_filepaths)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    app()
