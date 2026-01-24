import pytest

from matecon.io.excel_reader import ExcelReader

BOOK_SAMPLE = "sample_data/BOOK_SAMPLE.xlsx"
TABLE_HEADER_1 = ("HEADER_1", "HEADER_2", "HEADER_3")


def test_excel_reader_file_not_found():
    """存在しないファイルで `FileNotFoundError` が発生"""
    with pytest.raises(FileNotFoundError):
        ExcelReader("phantom_file.xlsx")


def test_excel_reader_no_material_sheets():
    """有効なシートがないExcelで `ValueError` が発生"""
    with pytest.raises(ValueError, match="有効なシートが存在しません"):
        reader = ExcelReader("sample_data/NO_MATERIAL_SHEETS.xlsx")
        reader.load_booknode()


def test_excel_reader_valid_file():
    """正常なExcelファイルの読み込み"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
    book = reader.load_booknode()
    assert book.filename == "BOOK_SAMPLE.xlsx"
    assert book.name == "BOOK_SAMPLE"
    assert len(book) == 3
    assert len(book.sheets) == 3
    assert book[0].name == "TABLE_SAMPLE"
