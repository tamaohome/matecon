from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from matecon.io.excel_reader import is_valid_excel_file
from matecon.io.io import write_text_file
from matecon.models.material import Material
from matecon.utils.collections import PathSet


class Controller(QObject):
    """コントローラクラス"""

    excelFilesChanged = Signal(list)
    materialChanged = Signal(Material)

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

    def add_excel_file(self, filepath: Path) -> Path | None:
        """Excelファイルを追加"""
        try:
            if not is_valid_excel_file(filepath):
                raise ValueError(f"無効なExcelファイルです:\n{filepath}")
            if filepath in self._excel_files:
                raise ValueError(f"すでに追加済みのファイルです:\n{filepath}")

            # 追加の Excel ファイルを加えて、新しい Material を生成
            new_material = self._create_material(*self._excel_files, filepath)

            # Material の生成が成功したら、Excel リストと Material を更新
            self._excel_files.add(filepath)
            self.excelFilesChanged.emit(self._excel_files.to_list)  # 変更通知
            self._material = new_material
            self.materialChanged.emit(self._material)  # 変更通知

            print("ファイルを追加:", filepath)
            return filepath
        except Exception as e:
            self.on_error(OperationType.ADD_FILE, filepath, e)

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
        if filepath not in self._excel_files:
            return

        self._excel_files.remove(filepath)
        self.excelFilesChanged.emit(self._excel_files.to_list)  # 変更通知

        self._material = self._create_material(*self._excel_files)
        self.materialChanged.emit(self._material)  # 変更通知

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
        self._material = None
        self.materialChanged.emit(self._material)  # 変更通知

    def _create_material(self, *filepaths: Path) -> Material | None:
        """ファイルパスを基に `Material` オブジェクトを生成"""
        if not self._excel_files:
            return None
        return Material(*list(filepaths))

    @property
    def excel_files(self) -> list[Path]:
        """Excelファイルリスト"""
        return list(self._excel_files)

    @property
    def material(self) -> Material | None:
        """材片情報"""
        return self._material


class OperationType(Enum):
    """処理の種別"""

    ADD_FILE = auto()
    REMOVE_FILE = auto()
    CONVERT_TO_TEXT = auto()
