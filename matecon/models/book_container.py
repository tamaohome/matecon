from collections.abc import Sequence
from pathlib import Path

from matecon.io.excel_reader import BookNode, ExcelReader, SheetNode

type FileListType = Sequence[Path | str]


class BookContainer:
    """まてりある材片情報テーブルを管理するクラス"""

    def __init__(self, header: tuple[str, ...], filepaths: FileListType):
        self._header = header
        self._books: list[BookNode] = self._create_books(*filepaths)

    def _create_books(self, *filepaths: str | Path) -> list[BookNode]:
        """Excelファイルから `BookNode` のリストを生成する"""
        booknodes: list[BookNode] = []
        for filepath in filepaths:
            reader = ExcelReader(filepath, self.header)
            booknode = reader.load_booknode()
            booknodes.append(booknode)
        return booknodes

    @property
    def header(self) -> tuple[str, ...]:
        """テーブルヘッダーを返す"""
        return self._header

    @property
    def books(self) -> tuple[BookNode, ...]:
        """Excelファイルにより読み込まれた BookNode を全て返す"""
        return tuple(self._books)

    @property
    def sheets(self) -> tuple[SheetNode, ...]:
        """Excelファイルにより読み込まれた SheetNode を全て返す"""
        return tuple(sheet for book in self.books for sheet in book)

    @property
    def rows(self) -> tuple[tuple, ...]:
        return tuple(row for book in self.books for row in book.table)

    @property
    def filepaths(self) -> list[Path]:
        return [book.filepath for book in self.books]

    @property
    def filenames(self) -> list[str]:
        return [str(p.name) for p in self.filepaths]
