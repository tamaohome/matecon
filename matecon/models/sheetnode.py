from __future__ import annotations

from pprint import pformat
from typing import TYPE_CHECKING, overload

from anytree import NodeMixin

from matecon.models.material import Material
from matecon.models.position import Position
from matecon.models.types import CellType, RowType, TableType
from matecon.utils.strings import zen2han

if TYPE_CHECKING:
    from matecon.models.booknode import BookNode


class SheetNode(NodeMixin):
    """
    Excelシートを保持するノードクラス

    `ExcelReader` インスタンスの `load_booknode()` より生成する
    """

    def __init__(self, parent: BookNode, sheet_name: str, rows: TableType, _sentinel: object = None):
        super().__init__()
        # プライベートコンストラクタ処理
        from matecon.models.booknode import _SENTINEL as _BOOKNODE_SENTINEL

        if _sentinel is not _BOOKNODE_SENTINEL:
            raise TypeError("SheetNode は直接生成できません")
        self.parent = parent
        self._name = sheet_name
        self._rows = rows
        try:
            self._header_position = self._get_header_position()
            self._table = self._get_table()
        except ValueError:
            # ヘッダー行が存在しない場合、自ノードを破棄する
            self.parent = None

    def __str__(self):
        return pformat(self.table)[1:-1]

    def __len__(self):
        return len(self.table)

    @overload
    def __getitem__(self, index: int) -> RowType: ...
    @overload
    def __getitem__(self, index: slice) -> TableType: ...

    def __getitem__(self, index: int | slice) -> RowType | TableType:
        # スライス指定
        if isinstance(index, slice):
            return self.table[index]

        # インデックス指定
        if index < 0:
            index += len(self.table)
        if 0 <= index < len(self.table):
            return self.table[index]
        else:
            raise IndexError(f"SheetNode インデックス '{index}' が範囲外です")

    def __iter__(self):
        return iter(self.table)

    def cell(self, row_n: int, col_n: int) -> CellType | None:
        """セルの値を返す"""
        return self.table[row_n][col_n]

    def _get_header_position(self) -> Position:
        """ヘッダー開始位置を返す"""
        # ヘッダー行を探索
        for row_n, row in enumerate(self._rows):
            f_row = tuple(zen2han(c) for c in row)
            # 現在の行にヘッダーが存在しない場合はスキップ
            if not set(self.header).issubset(f_row):
                continue
            # ヘッダーの最初のセルを探索
            for col_n, cell in enumerate(f_row):
                if cell != self.header[0]:
                    continue
                return Position(row_n, col_n)

        # ヘッダーが存在しない場合はエラー
        raise ValueError("ヘッダー行が存在しません:", self.booknode.filepath)

    def _get_table(self) -> TableType:
        row_n, col_n = self.table_origin.to_tuple
        return tuple(row[col_n:] for row in self._rows[row_n:])

    @property
    def header_position(self) -> Position:
        """ヘッダー開始位置を返す"""
        return self._header_position

    @property
    def table_origin(self) -> Position:
        """テーブル開始位置を返す"""
        # ヘッダーセルの下のセル位置を返す
        return self.header_position + Position(1, 0)

    @property
    def table(self) -> TableType:
        return self._table

    @property
    def name(self) -> str:
        return self._name

    @property
    def booknode(self) -> BookNode:
        assert self.parent
        return self.parent

    @property
    def header(self) -> tuple:
        return self.booknode.header

    @property
    def material(self) -> Material:
        """材片情報ノード"""
        return Material(self.table)
