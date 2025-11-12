from matecon.material import Material, MaterialNode

MATERIAL_FILE = "sample_data/MATERIAL_SAMPLE.xlsx"


def test_material():
    mate = Material(MATERIAL_FILE)
    assert isinstance(mate.root, MaterialNode)
    mate.print_tree()
    assert len(mate.nodes) == 27


def test_material_node_detail():
    mate = Material(MATERIAL_FILE)
    node = mate.nodes[13]

    assert node.name == "PL"
    # assert node.node_type == MaterialNodeType.DETAIL
    assert node.level_names == ["サンプル橋", "上部構造", "主構造", "横桁", "中間横桁", "中間横桁 仕口", "PL"]
    print(node)

    # TODO: 図面表記フォーマットを実装
    # node.format_blueprint = "1 - CONN PL 160 x 9 x 640 (SM400A)"


def test_material_node_values():
    mate = Material(MATERIAL_FILE)
    node = mate.nodes[20]  # DETAIL
    print(node)
    assert node.values[0] == "PL"
    assert node.values[1] == 220
    assert node.values[2] == 4.5

    # TODO: 列名をキーとする辞書の実装
    # assert node.values["MARK"] == "PL"
    # assert node.values["S1"] == 220
    # assert node.values["S2"] == 4.5


def test_material_node_slice():
    mate = Material(MATERIAL_FILE)
    node = mate.nodes[20]  # DETAIL
    print(node)
    assert node.values[:6] == ["PL", 220, 4.5, None, None, 800]
    assert node.values[29:31] == ["M", "M"]


def test_material_tree():
    """材片情報のツリー構造"""
    mate = Material(MATERIAL_FILE)

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
    assert node_detail_1.name == "PL"
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


def test_material_node_level_names():
    mate = Material(MATERIAL_FILE)

    node = mate.nodes[2]
    assert node.name == "主構造"
    assert node.parent
    assert node.parent.name == "上部構造"
    assert node.parent.parent
    assert node.parent.parent.name == "サンプル橋"

    assert node.level_names == ["サンプル橋", "上部構造", "主構造"]
