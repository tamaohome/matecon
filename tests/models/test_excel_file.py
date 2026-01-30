import pytest

from matecon.models.excel_file import ExcelFile


def test_file_not_found():
    """存在しないファイルを指定すると `FileNotFoundError` が発生"""
    with pytest.raises(FileNotFoundError):
        ExcelFile("phantom_file.xlsx")


def test_open_dir():
    """ディレクトリを指定すると `IsADirectoryError` が発生"""
    with pytest.raises(IsADirectoryError):
        ExcelFile("sample_data/")


def test_open_invalid_ext():
    """無効な拡張子のファイルを指定すると `ValueError` が発生"""
    with pytest.raises(ValueError):
        ExcelFile("sample_data/MATERIAL_SAMPLE_1.txt")


def test_valid_file():
    """正常なExcelファイルの読み込み"""
    filepath = "sample_data/BOOK_SAMPLE.xlsx"
    excel_file = ExcelFile(filepath)
    assert str(excel_file) == filepath
    assert excel_file == ExcelFile(filepath)
