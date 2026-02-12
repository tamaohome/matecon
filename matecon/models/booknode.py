from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Final, overload

from anytree import NodeMixin

from matecon.models.excel_file import ExcelFile
from matecon.models.material import Material
from matecon.models.sheetnode import SheetNode
from matecon.models.types import SheetType

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
    def table(self) -> SheetType:
        """全シートのテーブルを結合したテーブル（ヘッダーを除く）"""
        return tuple(row for sheet in self.sheets for row in sheet.table)

    @property
    def material(self) -> Material:
        """材片情報ノード"""
        return Material(self.table)
