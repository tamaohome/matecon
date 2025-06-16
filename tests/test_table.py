# -*- coding: utf-8 -*-

from matecon.table import Table
from matecon.spreadsheet import BookNode
from matecon.spreadsheet import SheetNode
from matecon.templates import TABLE_HEADER

MATERIAL_FILE = "sample_data/MATERIAL_SAMPLE.xlsx"
MATERIAL_FILE_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"


def test_table():
    # Table インスタンスの生成およびヘッダーの設定
    table = Table(header=TABLE_HEADER)
    assert table.header == TABLE_HEADER

    # Excelファイル追加前
    assert len(table.books) == 0  # 読み込んだExcelファイル数
    assert len(table.sheets) == 0  # 総シート数
    assert len(table.rows) == 0  # 総行数

    # Excelファイル追加後
    table.add_book(MATERIAL_FILE, MATERIAL_FILE_2)
    assert len(table.books) == 2  # 読み込んだExcelファイル数
    assert len(table.sheets) == 3  # 総シート数
    assert len(table.rows) == 50  # 総行数
    assert table.filenames == ["MATERIAL_SAMPLE.xlsx", "MATERIAL_SAMPLE_2.xlsx"]
