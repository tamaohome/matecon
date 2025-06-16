# -*- coding: utf-8 -*-

import sys
import warnings

# openpyxl の警告を無視
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

from PySide6.QtWidgets import QApplication

from .material import Material
from .utils import get_path_list
from .utils import write_txt
from .gui import MainWindow


def gui_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def cui_app():
    xlsx_files = get_path_list(".xlsx")
    mate = Material(xlsx_files[0])
    write_txt(xlsx_files[0], mate.format_lines)


if __name__ == "__main__":
    if "--cui" in sys.argv:
        cui_app()
    else:
        gui_app()
