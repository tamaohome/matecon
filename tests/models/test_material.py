# import pytest

from matecon.models.excel_file import ExcelFile
from matecon.models.excel_file_set import ExcelFileSet
from matecon.models.material import DetailNode, Material, MaterialNode

MATERIAL_XLSX_1 = "sample_data/MATERIAL_SAMPLE_1.xlsx"
MATERIAL_XLSX_2 = "sample_data/MATERIAL_SAMPLE_2.xlsx"
PHANTOM_XLSX = "sample_data/PHANTOM_FILE.xlsx"


def test_material():
    """正常なExcelファイルの読み込み"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1), ExcelFile(MATERIAL_XLSX_2)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    assert isinstance(mate.root, MaterialNode)
    assert len(mate.nodes) == 43


def test_material_node_detail():
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    node = mate.nodes[13]

    assert node.name == "1 - PL 160 x 9 x 640 (SS400)"
    assert node.hierarchy_names == [
        "サンプル橋",
        "上部構造",
        "主構造",
        "横桁",
        "中間横桁",
        "中間横桁 仕口",
        "1 - PL 160 x 9 x 640 (SS400)",
    ]


def test_material_line_for_drawing():
    """図面用フォーマット"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)

    node_1 = mate.nodes[13]
    assert isinstance(node_1, DetailNode)
    assert node_1.line_for_drawing() == "1 - PL 160 x 9 x 640 (SS400)"
    assert node_1.line_for_drawing(compact=True) == "1-PL160x9x640(SS400)"

    node_2 = mate.nodes[22]
    assert isinstance(node_2, DetailNode)
    assert node_2.line_for_drawing() == "16 - BN2 M12 x 45 (4.6)"


def test_material_node_values():
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    node = mate.nodes[20]
    assert isinstance(node, DetailNode)
    assert node.values[0] == "PL"
    assert node.values[1] == 220
    assert node.values[2] == 4.5

    # TODO: 列名をキーとする辞書の実装
    # assert node.values["MARK"] == "PL"
    # assert node.values["S1"] == 220
    # assert node.values["S2"] == 4.5


def test_material_node_slice():
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    node = mate.nodes[20]
    assert isinstance(node, DetailNode)
    assert node.values[:6] == ["PL", 220, 4.5, None, None, 800]
    assert node.values[29:31] == ["M", "M"]


def test_material_tree():
    """材片情報のツリー構造"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)

    # #1 サンプル橋
    node_level_1 = mate.nodes[0]
    assert node_level_1.name == "サンプル橋"
    assert node_level_1.level == 1
    assert len(node_level_1) == 1

    # #2 上部構造
    node_level_2 = node_level_1.children[0]
    assert node_level_2.name == "上部構造"
    assert node_level_2.level == 2
    assert len(node_level_2) == 2

    # #3 主構造
    node_level_3 = node_level_2.children[0]
    assert node_level_3.name == "主構造"
    assert node_level_3.level == 3
    assert len(node_level_3) == 1

    # #4 横桁
    node_level_4 = node_level_3.children[0]
    assert node_level_4.name == "横桁"
    assert node_level_4.level == 4
    assert len(node_level_4) == 1

    # #5 中間横桁
    node_level_5 = node_level_4.children[0]
    assert node_level_5.name == "中間横桁"
    assert node_level_5.level == 5
    assert len(node_level_5) == 2

    # BLOCK 中間横桁 本体
    node_block = node_level_5.children[0]
    assert node_block.name == "中間横桁 本体"
    assert node_block.names == ["中間横桁", "本体"]
    assert node_block.level == 6
    assert len(node_block) == 4

    # DETAIL (1) PL
    node_detail_1 = node_block.children[0]
    assert node_detail_1.is_leaf  # PaintNode がが存在しないため、末端ノード
    assert node_detail_1.name == "2 - PL 220 x 16 x 2200 (SM490YA)"
    assert node_detail_1.level == 7

    # DETAIL (2) PL
    node_detail_2 = node_block.children[1]
    assert not node_detail_2.is_leaf  # PaintNode が存在するため、末端ノードではない
    assert len(node_detail_2) == 2

    # PAINT *=
    node_paint = node_detail_2.children[0]
    assert node_paint.is_leaf  # PaintNode は常に末端ノード
    assert node_paint.name == "*="
    assert node_paint.level == 8


def test_material_node_hirrarchy_names():
    """材片情報ノードの階層名称リスト"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)

    node = mate.nodes[2]
    assert node.name == "主構造"
    assert node.parent
    assert node.parent.name == "上部構造"
    assert node.parent.parent
    assert node.parent.parent.name == "サンプル橋"

    assert node.hierarchy_names == ["サンプル橋", "上部構造", "主構造"]


def test_material_node_each():
    """材片情報ノードの員数"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    assert mate.nodes[4].each == 1  # LEVEL5
    assert mate.nodes[5].each == 6  # BLOCK (6*1)
    assert mate.nodes[6].each == 2  # DETAIL
    assert mate.nodes[8].each == 2  # PAINT
    assert mate.nodes[12].each == 12  # BLOCK (6*2)


def test_material_level_label():
    """材片情報レベル表示"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    assert mate.nodes[0].level_label == "#1"
    assert mate.nodes[1].level_label == "#2"
    assert mate.nodes[2].level_label == "#3"
    assert mate.nodes[3].level_label == "#4"
    assert mate.nodes[4].level_label == "#5"
    assert mate.nodes[5].level_label == "BLOCK"
    assert mate.nodes[6].level_label == "DETAIL"
    assert mate.nodes[8].level_label == "PAINT"


def test_material_name_with_level():
    """材片情報ノードの名称＋レベル名を返す"""
    excel_files = [ExcelFile(MATERIAL_XLSX_1)]
    excel_file_set = ExcelFileSet(excel_files)
    mate = Material(excel_file_set)
    assert mate.nodes[4].name_with_level == "#5 中間横桁"  # LEVEL5
    assert mate.nodes[5].name_with_level == "中間横桁 本体"  # BLOCK
    assert mate.nodes[6].name_with_level == "2 - PL 220 x 16 x 2200 (SM490YA)"  # DETAIL
    assert mate.nodes[8].name_with_level == "*="  # PAINT


def test_material_add():
    """`Material` を加算処理によりマージする"""
    file_set_1 = ExcelFileSet([ExcelFile(MATERIAL_XLSX_1)])
    mate_1 = Material(file_set_1)
    file_set_2 = ExcelFileSet([ExcelFile(MATERIAL_XLSX_2)])
    mate_2 = Material(file_set_2)

    mate = mate_1 + mate_2
    assert len(mate.nodes) == 43
