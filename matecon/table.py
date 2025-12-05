from pathlib import Path

from matecon.spreadsheet import BookNode, SheetNode


class Table:
    """まてりある材片情報テーブルを管理するクラス"""

    def __init__(self, header: tuple[str, ...]):
        self._header = header
        self._books = []

    def add_book(self, *filepaths: str | Path) -> None:
        """Excelファイルを追加する"""
        for filepath in filepaths:
            self._books.append(BookNode(filepath, self.header))

    def add_books(self, filepaths: list[Path] | tuple[Path, ...]) -> None:
        """Excelファイルを全て追加する"""
        self.add_book(*filepaths)

    @property
    def header(self) -> tuple[str, ...]:
        """テーブルヘッダーを返す"""
        return self._header

    @property
    def books(self) -> list[BookNode]:
        """Excelファイルにより読み込まれた BookNode を全て返す"""
        return self._books

    @property
    def sheets(self) -> list[SheetNode]:
        """Excelファイルにより読み込まれた SheetNode を全て返す"""
        return [sheet for book in self.books for sheet in book]

    @property
    def rows(self) -> tuple[tuple, ...]:
        return tuple(row for book in self.books for row in book.table)

    @property
    def filepaths(self) -> list[Path]:
        return [book.filepath for book in self.books]

    @property
    def filenames(self) -> list[str]:
        return [str(p.name) for p in self.filepaths]
