# -*- coding: utf-8 -*-

from matecon.position import Position
from matecon.spreadsheet import BookNode
from matecon.spreadsheet import SheetNode
from matecon.templates import TABLE_HEADER

SAMPLE_FILE = "sample_data/BOOK_SAMPLE.xlsx"
TABLE_HEADER1 = ("HEADER_1", "HEADER_2", "HEADER_3")
TABLE_HEADER2 = ("種類", "ゼロ値", "正数", "負数", "小数丸め", "関数", "表示形式1", "表示形式2")

MATERIAL_FILE = "sample_data/MATERIAL_SAMPLE.xlsx"
MATERIAL_FILE2 = "sample_data/MATERIAL_SAMPLE2.xlsx"


def test_booknode():
    """BookNode の読み込み"""
    book = BookNode(SAMPLE_FILE, TABLE_HEADER1)
    assert book.filename == "BOOK_SAMPLE.xlsx"
    assert book.name == "BOOK_SAMPLE"
    sheets = [sheet for sheet in book if isinstance(sheet, SheetNode)]
    assert len(sheets) == 1


def test_sheetnode():
    """SheetNode の読み込み"""
    sheet1 = BookNode(SAMPLE_FILE, TABLE_HEADER1)[0]
    assert sheet1.name == "TABLE_SAMPLE"

    sheet2 = BookNode(SAMPLE_FILE, TABLE_HEADER2)[0]
    assert sheet2.name == "CELL_TYPE"


def test_sheetnode_material():
    book = BookNode(MATERIAL_FILE, TABLE_HEADER)

    assert book[0].name == "横桁"
    assert book[1].name == "排水装置"
    assert len(book.table) == 33


def test_header_template():
    """ヘッダーテンプレート"""
    book = BookNode(SAMPLE_FILE, TABLE_HEADER1)
    sheet = book["TABLE_SAMPLE"]

    assert sheet.header_position == Position(5, 2)  # テーブルの開始位置
    assert sheet.table_origin == Position(6, 2)  # テーブルの開始位置
    assert sheet.table


def test_table_values():
    """テーブルおよびセル値の取得"""
    sheet = BookNode(SAMPLE_FILE, TABLE_HEADER1)["TABLE_SAMPLE"]

    assert sheet[0][0] == "CELL_01"
    assert sheet[2][0] == "CELL_21"
    assert sheet[3][-1] == "CELL_33"
    assert sheet[-1][0] == "END_CELL"

    assert len(sheet) == 5
    assert len(sheet[0]) == 3


def test_table_cell_types():
    """セル要素の型"""
    sheet = BookNode(SAMPLE_FILE, TABLE_HEADER2)["CELL_TYPE"]

    def assert_value_and_type(object, value, type=None):
        assert object == value
        if type:
            assert isinstance(object, type)

    assert_value_and_type(sheet[0][0], "INT", str)
    assert_value_and_type(sheet[0][1], 0, int)
    assert_value_and_type(sheet[0][2], 120, int)
    assert_value_and_type(sheet[0][3], -5, int)
    assert_value_and_type(sheet[0][4], 1234.5678, float)

    assert_value_and_type(sheet[1][0], "FLOAT", str)
    assert_value_and_type(sheet[1][1], 0, int)
    assert_value_and_type(sheet[1][2], 12, int)
    assert_value_and_type(sheet[1][3], -4.503, float)
    assert_value_and_type(sheet[1][4], 1.2345678, float)

    assert_value_and_type(sheet[2][0], "STR1", str)
    assert_value_and_type(sheet[2][1], "0", str)
    assert_value_and_type(sheet[2][2], "120", str)
    assert_value_and_type(sheet[2][3], "-5", str)
    assert_value_and_type(sheet[2][4], None)
    assert_value_and_type(sheet[2][5], "F6", str)

    # TODO: 表示形式を適用した表示値を返すようにする
    # assert_value_and_type(sheet[0][4], 1234, int)


def test_iter_table():
    sheet = BookNode(SAMPLE_FILE, TABLE_HEADER2)["CELL_TYPE"]

    for row in sheet:
        print(row)
        assert isinstance(row, tuple)
