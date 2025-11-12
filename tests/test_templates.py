from matecon.spreadsheet import BookNode
from matecon.templates import TABLE_HEADER, format_line

MATERIAL_FILE = "sample_data/MATERIAL_SAMPLE.xlsx"


def test_templates():
    sample_row = [
        None, None, "", "MARK", "S1", "S2", "S3", "S4", "L", "EACH", "UNITW", "NET", "QUALITY",
        "REMARK", "COMMENT", "PR1", "PR2", "JV", "ALIAS", "P", "T", "C1", "A1", "C2", "A2", "WT",
        "WB", "WL", "WR", "YW", "YL", "HT", "FACE1", "FACE2", "BOLT", "PW", "BEND", "LC", "BODY",
        "WRT", "WRB", "WRL", "WRR"
        ]  # fmt: skip

    assert set(TABLE_HEADER).issubset(set(sample_row))
    assert not set(sample_row).issubset(set(TABLE_HEADER))


def test_template_from_spreadsheet():
    book = BookNode(MATERIAL_FILE, TABLE_HEADER)
    assert isinstance(book, BookNode)


def test_template_format_line():
    material_items: list[tuple] = [
        ("#1", "サンプル橋", None, None, None, None, 1),
        ("#2", "上部構造", None, None, None, None, 1),
        ("#3", "主構造", None, None, None, None, 1),
        ("#4", "横桁", None, None, None, None, 1),
        ("#5", "中間横桁", None, None, None, None, 1),
        (None, "中間横桁", "本体", None, None, None, 6, 1),
        ("PL", 220, 16, None, None, 2200, 2, None, None, "SM490YA", "FLG", None, "L", None, None,
         None, None, "%", "A", 100)
    ]  # fmt: skip

    format_lines = [
        "#1   サンプル橋                   1",
        "#2   上部構造                     1",
        "#3   主構造                       1",
        "#4   横桁                         1",
        "#5   中間横桁                     1",
        "     中間横桁本体                 6",
        "PL    220  16          2200   2         SM490YA          FLG             L      %A  100",
    ]

    assert format_line(material_items[0]) == format_lines[0]
    assert format_line(material_items[6]) == format_lines[6]


# まてりあるの不具合: ブロック名称が3番目まで指定されている場合、2番目の員数が1に固定される
