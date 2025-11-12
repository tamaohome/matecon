from math import prod
from pathlib import Path
from typing import Final, Optional

from anytree import NodeMixin, RenderTree

from . import templates
from .table import Table


class Material:
    """
    材片情報ノードの管理クラス
    """

    def __init__(self, *filenames: str | Path):
        self.table = Table(templates.TABLE_HEADER)
        self.table.add_books(filenames)
        self.root = self._build_tree(self.table)

    def print_tree(self) -> None:
        """ツリーを表示"""
        print(self.table.filenames)
        for pre, _, node in RenderTree(self.root):
            if node.parent is None:
                continue
            print(f"{pre}{node.level} {node.name}")

    def _build_tree(self, table: Table) -> "MaterialNode":
        # ルートノード
        root = MaterialNode(parent=None, level=0, row=[])

        # 階層毎の最新ノードを格納する辞書
        level_nodes = {0: [root]}

        # ノードツリーの構築
        for row in table.rows:
            level = templates.level_detector(row)

            if level is None:
                continue

            # 親ノードの決定（同階層のノードリストのうち最新ノードを抽出）
            parent = level_nodes[level - 1][-1]

            # ノードの生成
            node = MaterialNode.create(parent, level, row)

            # 階層が重複するLEVELノードの場合は除外する
            if isinstance(node, LevelNode) and node.level_names in [n.level_names for n in node.siblings]:
                node.remove()
                continue

            # 最新ノードを格納する辞書の更新
            if level in level_nodes:
                level_nodes[level].append(node)
            else:
                level_nodes[level] = [node]

        return root

    @property
    def nodes(self) -> tuple["MaterialNode", ...]:
        """材片情報ノードを全て配列として返す"""
        return self.root.descendants

    @property
    def format_lines(self) -> list[str]:
        if self.root.is_leaf:
            raise ValueError("Material: 材片テーブルが存在しません")

        header = [
            "!TITLE    " + self.root.children[0].name,
            "!USER     STD",
            "!RANGE    0",
            "@VERSION  2",
        ]

        # MaterialNode を固定長文字列にフォーマットして配列に追加
        lines = self.root.format_lines

        return header + lines

    @property
    def filenames(self) -> list[str]:
        return self.table.filenames


def check_not_root(func):
    def wrapper(self, *args, **kwargs):
        if self.parent is None:
            raise ValueError("ルートノードです")
        return func(self, *args, **kwargs)

    return wrapper


class MaterialNode(NodeMixin):
    """材片情報ノードクラス"""

    def __init__(self, parent: Optional["MaterialNode"], level: int, row: list | tuple):
        super().__init__()
        self.parent = parent
        self.level: Final[int] = level
        self._row = list(row)

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        return self.__class__.__name__ + f'(name="{self.name}", level={self.level}, values={str(self._row)})'

    def remove(self) -> None:
        self.parent = None

    @staticmethod
    def create(parent: Optional["MaterialNode"], level: int, row: list | tuple) -> "MaterialNode":
        """`level` に基づいて `MaterialNode` またはサブクラスを作成"""
        if parent is None:
            return MaterialNode(parent, level, row)

        match level:
            case 1 | 2 | 3 | 4 | 5:
                return LevelNode(parent, level, row)
            case 6:
                assert isinstance(parent, LevelNode)
                return BlockNode(parent, row)
            case 7:
                assert isinstance(parent, BlockNode)
                return DetailNode(parent, row)
            case 8:
                assert isinstance(parent, DetailNode)
                return PaintNode(parent, row)

        raise ValueError(f"MaterialNodeの生成に失敗しました (level={level})")

    @property
    def descendants(self) -> tuple["MaterialNode", ...]:
        return super().descendants

    @property
    def children(self) -> tuple["MaterialNode", ...]:
        return super().children

    @property
    def format_lines(self) -> list[str]:
        """自ノードおよび子ノードを固定長文字列のリストとして返す"""
        # 自ノード
        lines = []
        if not self.is_root:
            lines.append(self.format_line)

        # 子ノード
        for child in self.children:
            lines.extend(child.format_lines)

        return lines

    @property
    @check_not_root
    def format_line(self) -> str:
        """自ノードを固定長文字列として返す"""
        return templates.format_line(self._row)

    @property
    def values(self) -> list:
        return self._row

    @property
    @check_not_root
    def names(self) -> list[str]:
        """自ノードの名称をリストで返す"""
        return [self._row[0]]

    @property
    @check_not_root
    def name(self) -> str:
        """
        自ノードの名称を返す

        - LEVEL: レベル名
        - BLOCK: ブロック名
            （ブロック名が複数存在する場合、半角スペースで結合した文字列として返す）
        - DETAIL: 材片名
        """
        return " ".join(self.names)

    @property
    @check_not_root
    def level_names(self) -> list[str]:
        """自ノードまでの階層名称をリストとして返す"""
        return [n.name for n in self.path if not n.is_root]


class LevelNode(MaterialNode):
    """
    材片情報ノードクラス (LEVEL)

    0列目にレベル階層("#1"〜"#5")が存在する行に対して LevelNode が生成される
    """

    def __init__(self, parent: MaterialNode, level: int, row: list | tuple):
        super().__init__(parent, level, row)

    @property
    def names(self) -> list[str]:
        return [str(self._row[1])]


class BlockNode(MaterialNode):
    """
    ブロック情報ノードクラス (BLOCK)

    `MARK`(材片名) に空白("")、`S1`(形状寸法(S1)) にブロック名が存在する行に対して BlockNode が生成される
    """

    def __init__(self, parent: LevelNode, row: list | tuple):
        super().__init__(parent, 6, row)

    @property
    def names(self) -> list[str]:
        """自ノードの名称を要素数 1〜3 のリストで返す"""
        return [str(cell) for cell in self._row[1:4] if cell]

    @property
    def format_line(self) -> str:
        """
        自ノードを固定長文字列として返す

        BLOCKの場合は員数 1〜3 を集計する
        - example: 員数列 `[6, 1, 2]` -> `[12, None, None]`
        """
        block_num = prod(n for n in self._row[6:9] if n)
        row = self._row
        row[6:9] = [block_num, None, None]

        return templates.format_line(row)

    @property
    def format_lines(self) -> list[str]:
        """
        自ノードおよび子ノードを固定長文字列のリストとして返す

        BlockNode の場合は末尾に "END" 行を追加する
        """

        return super().format_lines + ["END"]


class DetailNode(MaterialNode):
    """
    材片情報ノードクラス (DETAIL)

    ブロック行以下の行に対して `DetailNode`(材片情報ノード) または `PaintNode`(塗装情報ノード) が生成される
    """

    def __init__(self, parent: BlockNode, row: list | tuple):
        super().__init__(parent, 7, row)

    def __repr__(self):
        return "DetailNode()"


class PaintNode(MaterialNode):
    """
    塗装情報ノードクラス (PAINT)

    `MARK`(材片名) に `*=` がが存在する行に対して `PaintNode`(塗装情報ノード) が生成される
    """

    def __init__(self, parent: DetailNode, row: list | tuple):
        super().__init__(parent, 8, row)
