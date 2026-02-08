from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from pprint import pformat
from typing import Final, overload

from anytree import NodeMixin
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.cell.read_only import EmptyCell, ReadOnlyCell

from matecon.models.excel_file import ExcelFile
from matecon.models.position import Position
from matecon.utils.strings import zen2han

type ExcelCell = Cell | ReadOnlyCell | MergedCell | EmptyCell

type CellType = str | int | float
type RowType = tuple[CellType | None, ...]
type SheetType = tuple[RowType, ...]

ALLOW_EXTS = [".xlsx", ".xlsm"]
_SENTINEL = object()  # プライベートコンストラクタ用


class BookNode(NodeMixin):
    """
    Excelブックを保持するノードクラス

    `ExcelReader` インスタンスの `load_booknode()` より生成する
    """

    def __init__(self, excel_file: ExcelFile, header: tuple[str, ...], _sentinel: object = None):
        super().__init__()
        # プライベートコンストラクタ処理
        if _sentinel is not _SENTINEL:
            raise TypeError("BookNode は直接生成できません")

        self.excel_file: Final = excel_file
        self.header: Final = header

    @overload
    def __getitem__(self, key: int) -> SheetNode: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[SheetNode, ...]: ...
    @overload
    def __getitem__(self, key: str) -> SheetNode: ...

    def __getitem__(self, key: int | str | slice) -> SheetNode | tuple[SheetNode, ...]:
        # スライス指定
        if isinstance(key, slice):
            return self.sheets[key]

        # インデックス指定
        if isinstance(index := key, int):
            if index < 0:
                index += len(self.sheets)
            if 0 <= index < len(self.sheets):
                return self.sheets[index]
            else:
                raise IndexError(f"BookNode インデックス '{index}' が範囲外です")

        # キー指定
        if isinstance(name := key, str):
            for sheet in self:
                if sheet.name == name:
                    return sheet
            raise KeyError(f"シート名 '{name}' が見つかりません")

        raise TypeError("key には int | str | slice 型を指定してください")

    def __len__(self):
        return len(self.sheets)

    def __iter__(self) -> Iterator[SheetNode]:
        return iter(self.sheets)

    @property
    def name(self) -> str:
        """ファイル名（拡張子を含まない）"""
        return self.excel_file.filepath.stem

    @property
    def filename(self) -> str:
        """ファイル名（拡張子を含む）"""
        return self.excel_file.filepath.name

    @property
    def filepath(self) -> Path:
        """ファイルパス"""
        return Path(self.excel_file.filepath)

    @property
    def sheets(self) -> tuple[SheetNode]:
        """Excelシートのリスト"""
        return self.children

    @property
    def valid_sheets(self) -> tuple[SheetNode]:
        """有効なExcelシートのリスト"""
        # TODO: バリデーションを追加
        return self.sheets

    @property
    def table(self) -> tuple[RowType, ...]:
        """全シートのテーブルを結合したテーブル（ヘッダーを除く）"""
        return tuple(row for sheet in self.sheets for row in sheet.table)


class SheetNode(NodeMixin):
    """
    Excelシートを保持するノードクラス

    `ExcelReader` インスタンスの `load_booknode()` より生成する
    """

    def __init__(self, parent: BookNode, sheet_name: str, rows: SheetType, _sentinel: object = None):
        super().__init__()
        # プライベートコンストラクタ処理
        if _sentinel is not _SENTINEL:
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
    def __getitem__(self, index: slice) -> SheetType: ...

    def __getitem__(self, index: int | slice) -> RowType | SheetType:
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

    def _get_table(self) -> SheetType:
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
    def table(self) -> SheetType:
        return self._table

    @property
    def name(self) -> str:
        return self._name

    @property
    def booknode(self) -> BookNode:
        assert isinstance(self.parent, BookNode)
        return self.parent

    @property
    def header(self) -> tuple:
        return self.booknode.header
