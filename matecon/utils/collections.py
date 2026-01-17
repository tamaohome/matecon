from collections.abc import Iterable, MutableSet
from contextlib import suppress
from pathlib import Path

from boltons.setutils import IndexedSet


class PathSet(MutableSet[Path]):
    """
    ファイルパスを `Path` オブジェクトとして保持する順序付き集合クラス

    - `in` 演算子で中身を調べるときは `str | Path` を指定する
    """

    def __init__(self, filepaths: Iterable[str | Path] | None = None) -> None:
        self._inner: IndexedSet = IndexedSet()
        if not filepaths:
            return
        for p in filepaths:
            self.add(p)

    def add(self, filepath: str | Path) -> None:
        """ファイルパスを追加する"""
        if not isinstance(filepath, (str, Path)):
            raise TypeError(f"str または Path が必要です: {type(filepath).__name__}")
        resolved_path = Path(filepath).resolve(strict=False)
        self._inner.add(resolved_path)

    def discard(self, filepath: str | Path) -> None:
        """ファイルパスを削除する"""
        resolved_path = Path(filepath).resolve(strict=False)
        with suppress(KeyError):
            self._inner.remove(resolved_path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self._inner)})"

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index: int) -> Path:
        return self._inner[index]

    def __iter__(self) -> Iterable[Path]:
        return iter(self._inner)

    def __contains__(self, item: str | Path) -> bool:
        norm_path = Path(item).resolve(strict=False)
        return norm_path in self._inner

    @property
    def to_list(self) -> list[Path]:
        return list(self._inner)
