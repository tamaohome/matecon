from matecon.models.book_container import BookContainer
from matecon.models.excel_file import ExcelFile
from matecon.models.excel_file_set import ExcelFileSet
from matecon.models.templates import MATERIAL_HEADER

MATERIAL_XLSX_1 = "sample_data/material_data_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/material_data_2.xlsx"


def test_book_container():
    filepaths = [MATERIAL_XLSX_1, MATERIAL_XLSX_2]
    excel_files = [ExcelFile(f) for f in filepaths]
    excel_file_set = ExcelFileSet(excel_files)
    container = BookContainer(excel_file_set, MATERIAL_HEADER)
    assert container.header == MATERIAL_HEADER

    assert len(container.books) == 2  # 読み込んだExcelファイル数
    assert len(container.sheets) == 3  # 総シート数（有効シートのみ）
    assert len(container.rows) == 56  # 総行数（空白行を含む）
    assert container.filenames == ["material_data_1.xlsx", "material_data_2.xlsx"]
