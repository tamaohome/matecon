import pytest

from matecon.io.excel_reader import WorkbookReader
from matecon.models.excel_file import ExcelFile

BOOK_SAMPLE = "sample_data/book_sample.xlsx"
NO_MATERIAL_SHEETS = "sample_data/no_material_sheets.xlsx"
TABLE_HEADER_1 = ("HEADER_1", "HEADER_2", "HEADER_3")


def test_workbook_reader_no_material_sheets():
    """有効なシートがないExcelを指定すると `ValueError` が発生"""
    with pytest.raises(ValueError, match="有効なシートが存在しません"):
        excel_file = ExcelFile(NO_MATERIAL_SHEETS)
        reader = WorkbookReader(excel_file)
        reader.load_booknode()


def test_workbook_reader_valid_file():
    """正常なExcelファイルの読み込み"""
    excel_file = ExcelFile(BOOK_SAMPLE)
    reader = WorkbookReader(excel_file, TABLE_HEADER_1)
    book = reader.load_booknode()
    assert book.filename == "book_sample.xlsx"
    assert book.name == "book_sample"
    assert len(book) == 3
    assert len(book.sheets) == 3
    assert book[0].name == "TABLE_SAMPLE"
