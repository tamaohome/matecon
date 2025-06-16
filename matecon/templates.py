# -*- coding: utf-8 -*-

from enum import Enum, auto
from dataclasses import dataclass
from typing import TypeAliasType
from typing import Optional

from .strings import adjust_str


class MaterialNodeType(Enum):
    """行の形式"""

    HEADER = auto()
    LEVEL = auto()
    BLOCK = auto()
    # GROUP = auto()  # GROUP行はスプレッドシートでは存在しない
    DETAIL = auto()
    PAINT = auto()
    EMPTY = auto()
    NONE = auto()

    @property
    def name(self) -> str:
        return self.name.lower()

    @property
    def templates(self) -> list["Template"]:
        return TEMPLATES[self]

    @property
    def table_header(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.templates)


def type_detector(row: list | tuple) -> Optional["MaterialNodeType"]:
    """行からノードタイプを返す"""
    if len(row) == 0:
        return None
    if row[0] in ["#1", "#2", "#3", "#4", "#5"]:
        return MaterialNodeType.LEVEL
    # if "END" in row[:2]:
    #     return MaterialNodeType.END
    if row[0] is None and isinstance(row[1], str):
        return MaterialNodeType.BLOCK
    if row[0] == "*=":
        return MaterialNodeType.PAINT
    if 2 < len(row) and all(row[:2]):
        return MaterialNodeType.DETAIL

    return None
    # raise ValueError("ノードタイプの検出に失敗しました")


def level_detector(row: list | tuple) -> Optional[int]:
    """
    行から階層レベルを返す
    - LEVEL:  1-5
    - BLOCK:  6
    - DETAIL: 7
    - PAINT:  8
    - その他: None
    """

    node_type = type_detector(row)

    match node_type:
        case MaterialNodeType.LEVEL:
            return int(row[0][1])
        case MaterialNodeType.BLOCK:
            return 6
        case MaterialNodeType.DETAIL:
            return 7
        case MaterialNodeType.PAINT:
            return 8

    return None


class Align(Enum):
    L = auto()
    R = auto()


type String = int | float | str | None
type Number = int | float | None


@dataclass
class Template:
    """要素情報のテンプレート"""

    # fmt: off
    name:       str                 # 要素の名称
    type_name:  TypeAliasType       # 要素の型
    _pos:       tuple[int, int]     # 要素の位置
    align:      Align               # 要素の位置揃え
    is_req:     bool                # 要素の必須項目の場合 True
    dd:         str                 # 要素の説明
    # fmt: on

    # pos は tuple として格納されるが slice として返す
    @property
    def pos(self) -> slice:
        return slice(self._pos[0], self._pos[1])

    @staticmethod
    def empty(pos=(0, 0)) -> "Template":
        """要素情報の空テンプレートを返す"""
        return Template("EMPTY", String, pos, Align.L, False, "EMPTY")


def format_line(row: list | tuple) -> str:
    row_type = type_detector(row)

    if row_type is None:
        return ""

    line = ""
    for element, template in zip(row, row_type.templates):
        line += adjust_str(element, template.pos, template.align)
    return line.rstrip()


TEMPLATES = {
    # fmt: off
    MaterialNodeType.LEVEL: [
        #        name      type    pos        align    is_req dd
        Template("TIER",   String, (  0,  5), Align.L, False, "レベル番号"),
        Template("NAME",   String, (  5, 30), Align.L, False, "レベル名称"),
        # TODO: セル位置によらず name による文字列フォーマット方式に変更する
        # TODO: この変更により、読み込むExcelの列を自由に変更可能
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template("N",      Number, ( 30, 35), Align.R, False, "レベル員数"),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template("JV",     String, ( 35, 37), Align.L, False, "JVコード"),
    ],
    MaterialNodeType.BLOCK: [
        #        name      type    pos        align    is_req dd
        Template.empty(            (  0,  5)),
        Template("NAME1",  String, (  5, 13), Align.L, False, "A0パート名称"),
        Template("NAME2",  String, ( 13, 21), Align.L, False, "A1パート名称"),
        Template("NAME3",  String, ( 21, 29), Align.L, False, "A2パート名称"),
        Template.empty(),
        Template.empty(),
        Template("NN1",    Number, ( 29, 35), Align.R, False, "ブロック員数1"),
        # Template("NN2",    Number, (  0,  0), Align.R, False, "ブロック員数2"),
        # Template("NN3",    Number, (  0,  0), Align.R, False, "ブロック員数3"),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(),
        Template.empty(            ( 35, 38)),
        Template("PB",     String, ( 38, 39), Align.L, False, "ブロック属性"),
        Template("JV",     String, ( 37, 39), Align.L, False, "JVコード"),
        Template("ALIAS",  String, ( 40, 43), Align.L, False, "計上ブロック別名"),
    ],
    # TODO: GROUP のテンプレートを追加
    MaterialNodeType.DETAIL: [
        #        name      type    pos        align    is_req dd
        Template("MARK",   String, (  0,  4), Align.L, True,  "形状記号"),
        Template("S1",     Number, (  4,  9), Align.R, False, "形状寸法(S1)"),
        Template("S2",     Number, (  9, 13), Align.R, False, "形状寸法(S2)"),
        Template("S3",     Number, ( 13, 17), Align.R, False, "形状寸法(S3)"),
        Template("S4",     Number, ( 17, 21), Align.R, False, "形状寸法(S4)"),
        Template("L",      Number, ( 21, 27), Align.R, False, "長さ"),
        Template("EACH",   Number, ( 27, 31), Align.R, True,  "員数"),
        Template("UNITW",  Number, ( 31, 37), Align.R, False, "単位重量"),
        Template("NET",    Number, ( 37, 40), Align.R, False, "ネット率"),
        Template("QUALITY",String, ( 40, 57), Align.L, True,  "材質記号"),
        Template("REMARK", String, ( 57, 65), Align.L, False, "材片名"),
        Template("COMMENT",String, ( 65, 73), Align.L, False, "コメント"),
        Template("PR1",    String, ( 73, 74), Align.L, True,  "材片属性1"),
        Template("PR2",    String, ( 74, 75), Align.L, False, "材片属性2"),
        Template("JV",     String, ( 75, 77), Align.L, False, "JVコード"),
        Template("ALIAS",  String, ( 77, 79), Align.L, False, "計上ブロック別名"),
        Template("P",      String, ( 79, 80), Align.L, False, "塗装区別コード"),
        Template("T",      String, ( 80, 81), Align.L, False, "塗装計算コード"),
        Template("C1",     String, ( 81, 82), Align.L, False, "塗装色コード1"),
        Template("A1",     Number, ( 82, 87), Align.R, False, "塗装色コード1塗装占有率"),
        Template("C2",     String, ( 87, 88), Align.L, False, "塗装色コード2"),
        Template("A2",     Number, ( 88, 93), Align.R, False, "塗装色コード2塗装占有率"),
        Template("WT",     String, ( 93, 94), Align.L, False, "上・溶接種類"),
        Template("WB",     String, ( 94, 95), Align.L, False, "下・溶接種類"),
        Template("WL",     String, ( 95, 96), Align.L, False, "左・溶接種類"),
        Template("WR",     String, ( 96, 97), Align.L, False, "右・溶接種類"),
        Template("YW",     Number, ( 97,101), Align.R, False, "余幅"),
        Template("YL",     Number, (101,105), Align.R, False, "余長"),
        Template("HT",     Number, (105,108), Align.R, False, "補正板厚"),
        Template("FACE1",  String, (108,109), Align.L, False, "表面処理(第1面)"),
        Template("FACE2",  String, (109,110), Align.L, False, "表面処理(第2面)"),
        Template("BOLT",   String, (110,111), Align.L, False, "単材本数対象"),
        Template("PW",     String, (111,112), Align.L, False, "板継ぎ溶接"),
        Template("BEND",   String, (112,113), Align.L, False, "曲げ加工"),
        Template("LC",     String, (113,114), Align.L, False, "レーザー加工"),
        Template("BODY",   String, (114,115), Align.L, False, "本体付き"),
        Template("WRT",    Number, (115,120), Align.R, False, "溶接延長の実長(上)"),
        Template("WRB",    Number, (120,125), Align.R, False, "溶接延長の実長(下)"),
        Template("WRL",    Number, (125,130), Align.R, False, "溶接延長の実長(左)"),
        Template("WRR",    Number, (130,135), Align.R, False, "溶接延長の実長(右)"),
    ],
    MaterialNodeType.PAINT: [
        #        name      type    pos        align    is_req dd
        Template("MARK",   String, (  0,  4), Align.L, True,  "形状記号"),
        Template("S1",     Number, (  4,  9), Align.R, False, "形状寸法(S1)"),
        Template("S2",     Number, (  9, 13), Align.R, False, "形状寸法(S2)"),
        Template("S3",     Number, ( 13, 17), Align.R, False, "形状寸法(S3)"),
        Template("S4",     Number, ( 17, 21), Align.R, False, "形状寸法(S4)"),
        Template("L",      Number, ( 21, 27), Align.R, False, "長さ"),
        Template("EACH",   Number, ( 27, 31), Align.R, True,  "員数"),
        Template("UNITW",  Number, ( 31, 37), Align.R, False, "単位重量"),
        Template("NET",    Number, ( 37, 40), Align.R, False, "ネット率"),
        Template("QUALITY",String, ( 40, 57), Align.L, True,  "材質記号"),
        Template("REMARK", String, ( 57, 65), Align.L, False, "材片名"),
        Template("COMMENT",String, ( 65, 73), Align.L, False, "コメント"),
        Template("PR1",    String, ( 73, 74), Align.L, True,  "材片属性1"),
        Template("PR2",    String, ( 74, 75), Align.L, False, "材片属性2"),
        Template("JV",     String, ( 75, 77), Align.L, False, "JVコード"),
        Template("ALIAS",  String, ( 77, 79), Align.L, False, "計上ブロック別名"),
        Template("P",      String, ( 79, 80), Align.L, False, "塗装区別コード"),
        Template("T",      String, ( 80, 81), Align.L, False, "塗装計算コード"),
        Template("C1",     String, ( 81, 82), Align.L, False, "塗装色コード1"),
        Template("A1",     Number, ( 82, 87), Align.R, False, "塗装色コード1塗装占有率"),
        Template("C2",     String, ( 87, 88), Align.L, False, "塗装色コード2"),
        Template("A2",     Number, ( 88, 93), Align.R, False, "塗装色コード2塗装占有率"),
    ],
    # fmt: on
}

TABLE_HEADER = MaterialNodeType.DETAIL.table_header
TABLE_HEADER_LEVEL = MaterialNodeType.LEVEL.table_header
TABLE_HEADER_BLOCK = MaterialNodeType.BLOCK.table_header
TABLE_HEADER_DETAIL = MaterialNodeType.DETAIL.table_header
TABLE_HEADER_PAINT = MaterialNodeType.PAINT.table_header
