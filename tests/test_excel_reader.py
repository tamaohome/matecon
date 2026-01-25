import pytest

from matecon.io.excel_reader import ExcelReader
from matecon.models.excel_file import ExcelFile

BOOK_SAMPLE = "sample_data/BOOK_SAMPLE.xlsx"
TABLE_HEADER_1 = ("HEADER_1", "HEADER_2", "HEADER_3")


def test_excel_reader_no_material_sheets():
    """有効なシートがないExcelを指定すると `ValueError` が発生"""
    with pytest.raises(ValueError, match="有効なシートが存在しません"):
        excel_file = ExcelFile("sample_data/NO_MATERIAL_SHEETS.xlsx")
        reader = ExcelReader(excel_file)
        reader.load_booknode()


def test_excel_reader_valid_file():
    """正常なExcelファイルの読み込み"""
    excel_file = ExcelFile(BOOK_SAMPLE)
    reader = ExcelReader(excel_file, TABLE_HEADER_1)
    book = reader.load_booknode()
    assert book.filename == "BOOK_SAMPLE.xlsx"
    assert book.name == "BOOK_SAMPLE"
    assert len(book) == 3
    assert len(book.sheets) == 3
    assert book[0].name == "TABLE_SAMPLE"
