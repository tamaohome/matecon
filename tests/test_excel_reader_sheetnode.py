import pytest

from matecon.io.excel_reader import ExcelReader, SheetNode
from matecon.models.position import Position
from matecon.models.templates import MATERIAL_HEADER

BOOK_SAMPLE = "sample_data/BOOK_SAMPLE.xlsx"
TABLE_HEADER_1 = ("HEADER_1", "HEADER_2", "HEADER_3")
TABLE_HEADER_2 = ("種類", "ゼロ値", "正数", "負数", "小数丸め", "関数", "表示形式1", "表示形式2")

MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"
MATERIAL_TXT_1 = "sample_data/MATERIAL_SAMPLE_1.txt"


def test_incorrect_node_creation():
    """`SheetNode` を直接生成した場合のエラー"""
    with pytest.raises(TypeError, match="SheetNode は直接生成できません"):
        reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
        booknode = reader.load_booknode()
        SheetNode(booknode, "title", ())


def test_sheetnode():
    """`SheetNode` の読み込み"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
    book = reader.load_booknode()
    assert book[0].name == "TABLE_SAMPLE"


def test_load_sheetnode():
    """Excelセルの読み込み"""
    reader = ExcelReader(MATERIAL_XLSX_1, MATERIAL_HEADER)
    book = reader.load_booknode()

    sheet = book[0]
    assert sheet.table_origin == Position(3, 3)
    assert sheet.cell(0, 0) == "#1"
    assert sheet[0][0] == "#1"


def test_load_table():
    """Excelテーブル（ヘッダーを除く）の読み込み"""
    reader = ExcelReader(MATERIAL_XLSX_1, MATERIAL_HEADER)
    book = reader.load_booknode()

    # テーブルの行数
    assert len(book[0].table) == 20
    assert len(book[1].table) == 17
    assert len(book.table) == 20 + 17


def test_header_template():
    """ヘッダーテンプレート"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
    sheet = reader.load_booknode()["TABLE_SAMPLE"]

    assert sheet.header

    assert sheet.header_position == Position(4, 1)  # ヘッダーの開始位置
    assert sheet.table_origin == Position(5, 1)  # テーブルの開始位置


def test_cell_values():
    """セルの値"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
    sheet = reader.load_booknode()["TABLE_SAMPLE"]

    # インデックス指定と cell() のいずれもセル参照可能
    assert sheet[0][0] is sheet.cell(0, 0)

    # テーブル（ヘッダーを除く）の要素として取得
    assert sheet[0][0] == "CELL_01"
    assert sheet[1][0] == "CELL_11"
    assert sheet[2][0] is None
    assert sheet[3][0] == "CELL_21"
    assert sheet[4][0] is None
    assert sheet[5][0] is None

    assert sheet[1][2] == "CELL_13"

    assert sheet[-2][-3] == "CELL_33"
    assert sheet[-2][-2] is None
    assert sheet[-2][-1] == "CELL_35"
    assert sheet[-1][0] == "END_CELL"

    assert len(sheet) == 8  # テーブル行数をチェック
    assert all(len(row) == 5 for row in sheet)  # テーブル各行の要素数をチェック


def test_cell_types():
    """セルの型"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_2)
    sheet = reader.load_booknode()["CELL_TYPE"]

    def assert_value_and_type(obj, value, value_type=None):
        assert obj == value
        if value_type is not None:
            assert isinstance(obj, value_type)

    assert_value_and_type(sheet[0][0], "INT", str)
    assert_value_and_type(sheet[0][1], 0, int)
    assert_value_and_type(sheet[0][2], 120, int)
    assert_value_and_type(sheet[0][3], -5, int)
    assert_value_and_type(sheet[0][4], 1234.5678, float)
    assert_value_and_type(sheet[0][5], 50, int)
    assert_value_and_type(sheet[0][6], 1234.5678, float)
    assert_value_and_type(sheet[0][7], 1234.5678, float)

    assert_value_and_type(sheet[1][0], "FLOAT", str)
    assert_value_and_type(sheet[1][1], 0, int)
    assert_value_and_type(sheet[1][2], 12, int)
    assert_value_and_type(sheet[1][3], -4.503, float)
    assert_value_and_type(sheet[1][4], 1.2345678, float)
    assert_value_and_type(sheet[1][5], 0.05, float)
    assert_value_and_type(sheet[1][6], 1.2345678, float)
    assert_value_and_type(sheet[1][7], 1234.5678, float)

    assert_value_and_type(sheet[2][0], "STR1", str)
    assert_value_and_type(sheet[2][1], "0", str)
    assert_value_and_type(sheet[2][2], "120", str)
    assert_value_and_type(sheet[2][3], "-5", str)
    assert_value_and_type(sheet[2][4], None)
    assert_value_and_type(sheet[2][5], "G6", str)

    assert_value_and_type(sheet[3][0], "STR2", str)
    assert_value_and_type(sheet[3][1], "0.00", str)
    assert_value_and_type(sheet[3][2], "12.00", str)
    assert_value_and_type(sheet[3][3], "-4.5030", str)


def test_merged_cell():
    """結合セル"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
    sheet = reader.load_booknode()["MERGED_CELLS"]

    assert sheet[0][0:3] == ("横に3マス結合", None, None)
    assert sheet[1:4] == (
        ("縦に3マス結合", None, None),
        (None, None, None),
        (None, None, None),
    )
    assert sheet[4:] == (
        ("縦横に結合", None, None),
        (None, None, None),
    )


def test_hidden_row():
    """非表示状態の行を取得"""
    reader = ExcelReader(BOOK_SAMPLE, TABLE_HEADER_1)
    sheet = reader.load_booknode()["HIDDEN_ROW"]

    assert sheet[0][0] == "A"
    assert sheet[1][0] == "B"
    assert sheet[2][0] == "C"
    assert sheet[3][0] == "D"  # 非表示状態の行
    assert sheet[4][0] == "E"
