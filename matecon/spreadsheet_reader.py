# -*- coding: utf-8 -*-

from pathlib import Path
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

READABLE_EXTS = [".xlsx", ".xlsm"]


class SpreadsheetReader:
    """Excelファイルを読み込むクラス"""

    wb: Workbook

    def __init__(self, filepath: str | Path):
        self.filepath = self._get_valid_filepath(filepath)

    def _get_valid_filepath(self, filepath: str | Path) -> Path:
        """チェックしたファイルパスを返す"""
        filepath = Path(filepath)

        # ファイルの存在チェック
        if not filepath.exists():
            raise FileNotFoundError("ファイルが見つかりません", filepath)

        # ファイル拡張子のチェック
        if filepath.is_file() and filepath.suffix.lower() not in READABLE_EXTS:
            raise ValueError("Excelファイルではありません", filepath)

        # ファイルオープンのチェック
        try:
            with open(filepath, "r"):
                pass
        except IOError:
            raise IOError("ファイルをオープンできません", filepath)

        return filepath

    def get_worksheets(self, ignore_hidden_sheet=True) -> list[Worksheet]:
        """
        シートのリストを取得する
        Arguments:
            ignore_hidden_sheet (bool): 非表示シートを無視するかどうか
        Returns:
            list[Worksheet]: ワークシートのリスト
        """
        self.wb = load_workbook(self.filepath, read_only=True, data_only=True)

        sheets: list[Worksheet] = []
        for worksheet in self.wb.worksheets:
            if not ignore_hidden_sheet or worksheet.sheet_state != "hidden":
                sheets.append(worksheet)
        return sheets

    def close(self) -> None:
        """ワークブックを閉じる"""
        self.wb.close()
