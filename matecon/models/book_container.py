from collections.abc import Collection
from functools import cached_property
from pathlib import Path
from typing import Final

from matecon.io.excel_reader import BookNode, ExcelReader, RowType, SheetNode
from matecon.models.excel_file import ExcelFile
from matecon.models.material import Material


class BookContainer:
    """まてりある用Excelファイルを管理するクラス"""

    def __init__(self, excel_files: Collection[ExcelFile], header: tuple[str, ...]):
        self._excel_file_set = excel_files
        self.header: Final = header
        self._books = self._create_books()

    def _create_books(self) -> list[BookNode]:
        """Excelファイルから `BookNode` のリストを生成する"""
        booknodes: list[BookNode] = []
        for excel_file in self._excel_file_set:
            reader = ExcelReader(excel_file, self.header)
            booknode = reader.load_booknode()
            booknodes.append(booknode)

            # 有効なシート一覧を更新 (ExcelFile)
            excel_file.valid_sheet_names = [sheet.name for sheet in booknode.valid_sheets]
        return booknodes

    @property
    def books(self) -> tuple[BookNode, ...]:
        """Excelファイルにより読み込まれた BookNode を全て返す"""
        return tuple(self._books)

    @property
    def sheets(self) -> tuple[SheetNode, ...]:
        """Excelファイルにより読み込まれた SheetNode を全て返す"""
        return tuple(sheet for book in self.books for sheet in book)

    @property
    def rows(self) -> tuple[RowType, ...]:
        return tuple(row for book in self.books for row in book.table)

    @property
    def excel_files(self) -> tuple[ExcelFile, ...]:
        return tuple(self._excel_file_set)

    @property
    def filepaths(self) -> list[Path]:
        return [book.filepath for book in self.books]

    @property
    def filenames(self) -> list[str]:
        return [str(p.name) for p in self.filepaths]

    @property
    def table(self) -> tuple[RowType, ...]:
        """全シートのテーブルを結合したテーブル（ヘッダーを除く）"""
        return tuple(row for sheet in self.sheets for row in sheet.table)

    @cached_property
    def material(self) -> Material:
        """材片情報ノード"""
        return Material(self.table)
