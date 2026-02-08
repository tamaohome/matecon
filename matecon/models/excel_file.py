from pathlib import Path
from typing import Final

ALLOW_EXTS = [".xlsx", ".xlsm"]


class ExcelFile:
    def __init__(self, filepath: str | Path) -> None:
        self.filepath: Final = Path(filepath)
        self.valid_sheet_names: list[str] = []
        self._validate()

    def __eq__(self, other) -> bool:
        if not isinstance(other, ExcelFile):
            return NotImplemented
        return self.filepath == other.filepath

    def __str__(self) -> str:
        return str(self.filepath)

    def __repr__(self) -> str:
        return f"ExcelFile({self.filepath!r})"

    def __hash__(self) -> int:
        return hash(self.filepath)

    def _validate(self) -> None:
        """ファイルの存在、拡張子、オープン可否をチェックする"""
        # ファイルの存在チェック
        if not self.filepath.exists():
            raise FileNotFoundError("ファイルが見つかりません", self.filepath)

        # ファイルであることをチェック
        if not self.filepath.is_file():
            raise IsADirectoryError("ファイルではありません", self.filepath)

        # ファイル拡張子のチェック
        if self.filepath.suffix.lower() not in ALLOW_EXTS:
            raise ValueError("Excelファイルではありません", self.filepath)

        # ファイルオープンのチェック
        try:
            with self.filepath.open(mode="r"):
                pass
        except OSError as e:
            raise OSError(f"ファイルをオープンできません: {e}") from e
