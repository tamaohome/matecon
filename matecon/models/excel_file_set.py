from __future__ import annotations

from collections.abc import Iterable, Iterator, MutableSet
from contextlib import suppress
from typing import override

from boltons.setutils import IndexedSet

from matecon.models.excel_file import ExcelFile


class ExcelFileSet(MutableSet[ExcelFile]):
    """
    ファイルパスを `ExcelFile` オブジェクトとして保持する順序付き集合クラス

    - `in` 演算子で中身を調べるときは `ExcelFile` を指定する
    """

    def __init__(self, excel_files: Iterable[ExcelFile] = []) -> None:
        self._inner: IndexedSet = IndexedSet()
        self.add(*excel_files)

    @override
    def add(self, *excel_files: ExcelFile) -> None:
        """`ExcelFile` オブジェクトを追加する"""
        for excel_file in excel_files:
            if excel_file in self._inner:
                raise ValueError(f"{excel_file}: 既に追加されているExcelファイルです")
            self._inner.add(excel_file)

    @override
    def discard(self, excel_file: ExcelFile) -> None:
        """
        `ExcelFile` オブジェクトを削除する

        Excelファイルが存在しない場合はエラーを発生せず処理を中止する
        """
        with suppress(KeyError):
            self._inner.remove(excel_file)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self._inner)})"

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index: int) -> ExcelFile:
        return self._inner[index]

    def __iter__(self) -> Iterator[ExcelFile]:
        return iter(self._inner)

    def __contains__(self, excel_file: ExcelFile) -> bool:
        return excel_file in self._inner

    def __add__(self, other: ExcelFile | ExcelFileSet) -> ExcelFileSet:
        """加算演算子で `ExcelFile | ExcelFileSet` を追加した新しいセットを返す"""
        new_set = ExcelFileSet(self)
        if isinstance(other, ExcelFile):
            new_set.add(other)
        elif isinstance(other, ExcelFileSet):
            for excel_file in other:
                new_set.add(excel_file)
        return new_set
