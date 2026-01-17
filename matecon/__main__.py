import sys
import warnings

from PySide6.QtWidgets import QApplication

from matecon.gui.view import MainWindow

# openpyxl の警告を無視
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    app()
