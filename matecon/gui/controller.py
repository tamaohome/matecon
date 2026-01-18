from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from matecon.io.io import write_text_file
from matecon.io.spreadsheet_reader import validate_excel_filepath
from matecon.models.material import Material
from matecon.utils.collections import PathSet


class Controller(QObject):
    """コントローラクラス"""

    excelFilesChanged = Signal(list)
    materialChanged = Signal(Material)
    treeExpandDepthChanged = Signal(int)

    def __init__(
        self,
        parent: QObject | None = None,
        on_success: Callable[[OperationType, Path, str], None] | None = None,
        on_error: Callable[[OperationType, Path, Exception], None] | None = None,
    ):
        super().__init__(parent)

        # コールバック関数
        self.on_success = on_success or (lambda *_: None)
        self.on_error = on_error or (lambda *_: None)

        # 状態管理変数
        self._material: Material | None = None  # 材片情報
        self._excel_files = PathSet()  # Excelファイルリスト
        self._tree_expand_depth = 6  # ツリー展開深さ

    def is_valid_excel_file(self, excel_filepath: str | Path) -> bool:
        """有効なExcelファイルの場合 `True` を返す"""
        try:
            validate_excel_filepath(excel_filepath)
            return True
        except (FileNotFoundError, ValueError, OSError):
            return False

    def add_excel_file(self, filepath: Path) -> Path:
        """Excelファイルを追加する"""
        try:
            if not self.is_valid_excel_file(filepath):
                raise ValueError(f"無効なExcelファイルです:\n{filepath}")
            if filepath in self._excel_files:
                raise ValueError(f"すでに追加済みのファイルです:\n{filepath}")

            self._excel_files.add(filepath)
            self._update_material()
            self.excelFilesChanged.emit(self._excel_files.to_list)  # 変更通知
            print("ファイルを追加:", filepath)
            return filepath
        except Exception as e:
            self.on_error(OperationType.ADD_FILE, filepath, e)
            raise

    def add_excel_files(self, filepaths: Sequence[Path]) -> list[Path]:
        """複数のExcelファイルを追加し、正常に追加したファイルパスのリストを返す"""
        added_files = []
        for filepath in filepaths:
            try:
                added_file = self.add_excel_file(filepath)
                added_files.append(added_file)
            except Exception:
                continue
        return added_files

    def remove_excel_file(self, filepath: Path) -> None:
        """リストからExcelファイルを取り除く"""
        try:
            if filepath not in self._excel_files:
                raise ValueError(f"ファイルがリストに存在しません:\n{filepath}")
            self._excel_files.remove(filepath)
            self._update_material()
            self.excelFilesChanged.emit(self._excel_files.to_list)  # 変更通知
            print("ファイルを除去:", filepath)
        except Exception as e:
            self.on_error(OperationType.REMOVE_FILE, filepath, e)
            raise

    def convert_to_text_file(self, overwrite_confirm: Callable[[Path], bool] | None = None) -> Path | None:
        """
        Excelファイルを JIP-まてりある用テキストファイルに変換

        変換後のテキストファイルのパスを返す
        """
        if self._material is None:
            message = "Excelファイルが存在しません"
            self.on_error(OperationType.CONVERT_TO_TEXT, Path(), ValueError(message))
            return

        # 最初のExcelファイルを基にテキストファイルのパスを取得
        output_path = self._excel_files[0].with_suffix(".txt")

        # 上書き時の処理
        if output_path.exists():
            if overwrite_confirm is None:
                return None
            if not overwrite_confirm(output_path):
                return None  # 上書きキャンセル時は処理を中止

        try:
            output_lines = self._material.format_lines
            result = write_text_file(output_path, output_lines)
            message = "テキストファイルに変換しました:\n" + str(result)
            self.on_success(OperationType.CONVERT_TO_TEXT, output_path, message)
            return result
        except Exception as e:
            self.on_error(OperationType.CONVERT_TO_TEXT, output_path, e)
            raise

    def clear_files(self) -> None:
        """追加されたExcelファイル一覧をクリア"""
        self._excel_files.clear()
        self.excelFilesChanged.emit(self._excel_files.to_list)  # 変更通知
        self._update_material()

    def _update_material(self) -> None:
        """現在のファイルパスリストを基に `Material` オブジェクトを更新する"""
        self._material = self._create_material()
        self.materialChanged.emit(self._material)  # 変更通知

    def _create_material(self) -> Material | None:
        """`Material` オブジェクトを生成"""
        if not self._excel_files:
            return None
        return Material(*list(self._excel_files))

    @property
    def excel_files(self) -> list[Path]:
        """Excelファイルリスト"""
        return list(self._excel_files)

    @property
    def material(self) -> Material | None:
        """材片情報"""
        return self._material

    @property
    def tree_expand_depth(self) -> int:
        """ツリー展開深さ"""
        return self._tree_expand_depth


class OperationType(Enum):
    """処理の種別"""

    ADD_FILE = auto()
    REMOVE_FILE = auto()
    CONVERT_TO_TEXT = auto()
