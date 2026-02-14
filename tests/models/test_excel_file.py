from pathlib import Path

import pytest

from matecon.models.excel_file import ExcelFile

MATERIAL_TXT_1 = "sample_data/material_data_1.txt"
BOOK_SAMPLE = "sample_data/book_sample.xlsx"


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
        ExcelFile(MATERIAL_TXT_1)


def test_valid_file():
    """正常なExcelファイルの読み込み"""
    filepath = Path(BOOK_SAMPLE)
    excel_file = ExcelFile(filepath)
    assert str(excel_file) == str(filepath)
