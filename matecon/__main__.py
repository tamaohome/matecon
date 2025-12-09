import sys
import warnings

from PySide6.QtWidgets import QApplication

from matecon.gui.controller import Controller
from matecon.gui.view import MainWindow
from matecon.utils.io import get_path_list

# openpyxl の警告を無視
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def gui_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def cui_app():
    xlsx_files = get_path_list(".xlsx")
    controller = Controller()
    try:
        controller.convert_file(str(xlsx_files[0]))
    finally:
        controller.cleanup()


if __name__ == "__main__":
    if "--cui" in sys.argv:
        cui_app()
    else:
        gui_app()
