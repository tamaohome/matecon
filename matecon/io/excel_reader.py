from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.cell.read_only import EmptyCell, ReadOnlyCell
from openpyxl.worksheet.worksheet import Worksheet

from matecon.models.booknode import _SENTINEL, BookNode, SheetNode
from matecon.models.templates import MATERIAL_HEADER

type ExcelCell = Cell | ReadOnlyCell | MergedCell | EmptyCell

type CellType = str | int | float
type RowType = tuple[CellType | None, ...]
type SheetType = tuple[RowType, ...]

ALLOW_EXTS = [".xlsx", ".xlsm"]


def is_valid_excel_file(excel_filepath: str | Path) -> bool:
    """有効なExcelファイルの場合 `True` を返す"""
    try:
        validate_excel_filepath(excel_filepath)
        return True
    except (FileNotFoundError, ValueError, OSError):
        return False


def validate_excel_filepath(filepath: str | Path) -> Path:
    """バリデーション済みのExcelファイルパスを返す"""
    filepath = Path(filepath)

    # ファイルの存在チェック
    if not filepath.exists():
        raise FileNotFoundError("ファイルが見つかりません", filepath)

    # ファイル拡張子のチェック
    if filepath.is_file() and filepath.suffix.lower() not in ALLOW_EXTS:
        raise ValueError("Excelファイルではありません", filepath)

    # ファイルオープンのチェック
    try:
        with open(filepath):
            pass
    except OSError as e:
        raise OSError(f"ファイルをオープンできません: {e}") from e

    return filepath


class ExcelReader:
    """Excelファイルを読み込むクラス"""

    def __init__(self, filepath: str | Path, header=MATERIAL_HEADER):
        self._filepath = validate_excel_filepath(filepath)
        self._header = header

    def load_booknode(self, ignore_hidden_sheet=True) -> BookNode:
        """Excelブックを取得する"""
        booknode = BookNode(self.filepath, self._header, _SENTINEL)
        try:
            wb = load_workbook(self.filepath, read_only=True, data_only=True)
            for worksheet in wb.worksheets:
                # 非表示シートの場合はスキップ
                if ignore_hidden_sheet and worksheet.sheet_state == "hidden":
                    continue
                self._set_sheetnode(booknode, worksheet)
        finally:
            wb.close()

        # 有効なシートが取得できなかった場合エラー
        if len(booknode) == 0:
            raise ValueError(f"{self.filepath}: 有効なシートが存在しません。")

        return booknode

    def _set_sheetnode(self, booknode: BookNode, worksheet: Worksheet) -> None:
        """Excelシートを `BookNode` にセットする"""
        rows_iterator = worksheet.iter_rows(values_only=True)
        rows = tuple(self._get_row(row) for row in rows_iterator)
        SheetNode(booknode, worksheet.title, rows, _SENTINEL)

    def _get_row(self, row: tuple) -> RowType:
        return tuple(self._get_cell(cell) for cell in row)

    def _get_cell(self, cell) -> CellType | None:
        """書式設定を考慮したセルの値を返す"""
        if isinstance(cell, MergedCell):  # 結合されたセルの場合
            input(f"MergedCellを検出: {cell}")
            return None
        if isinstance(cell, EmptyCell) or cell is None:  # 空白セルの場合
            return None
        if isinstance(cell, int):  # 整数の場合
            return cell
        if isinstance(cell, float):  # 小数を含む場合
            return cell
        return str(cell)  # それ以外は文字列型として返す

    @property
    def filepath(self) -> Path:
        """ファイルパス"""
        return self._filepath
