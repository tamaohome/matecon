from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from matecon.io.io import write_text_file
from matecon.models.excel_file import ExcelFile
from matecon.models.excel_file_set import ExcelFileSet
from matecon.models.material import Material


class Controller(QObject):
    """コントローラクラス"""

    excelFileSetChanged = Signal(list)
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
        self._excel_file_set = ExcelFileSet()  # Excelファイルセット

    def add_excel_file(self, filepath: Path | str) -> None:
        """Excelファイルを追加"""
        try:
            # 追加の Excel ファイルを加えて、新しい Material を生成
            new_excel_file = ExcelFile(filepath)
            new_set = self._excel_file_set + new_excel_file
            new_material = self._create_material(new_set)

            # Material の生成が成功したら、Excel リストと Material を更新
            self._excel_file_set.add(new_excel_file)
            self.excelFileSetChanged.emit(self._excel_file_set)  # 変更通知
            self._material = new_material
            self.materialChanged.emit(self._material)  # 変更通知

            print("ファイルを追加:", filepath)
            return
        except Exception as e:
            self.on_error(OperationType.ADD_FILE, Path(filepath), e)

    def add_excel_files(self, filepaths: Sequence[Path | str]) -> list[ExcelFile]:
        """複数のExcelファイルを追加し、正常に追加したファイルパスのリストを返す"""
        added_files = []
        for filepath in filepaths:
            try:
                added_file = self.add_excel_file(filepath)
                added_files.append(added_file)
            except Exception:
                continue
        return added_files

    def remove_excel_file(self, excel_file: ExcelFile) -> None:
        """リストからExcelファイルを取り除く"""
        if excel_file not in self._excel_file_set:
            return

        self._excel_file_set.remove(excel_file)
        self.excelFileSetChanged.emit(self._excel_file_set)  # 変更通知

        self._material = self._create_material(self._excel_file_set)
        self.materialChanged.emit(self._material)  # 変更通知

    def convert_to_text_file(self, overwrite_confirm: Callable[[Path], bool] | None = None) -> Path | None:
        """
        Excelファイルを JIP-まてりある用テキストファイルに変換

        変換後のテキストファイルのパスを返す
        """
        if self._material is None or not self._excel_file_set:
            error_message = "Excelファイルが存在しません"
            self.on_error(OperationType.CONVERT_TO_TEXT, Path(), ValueError(error_message))
            return

        # 最初のExcelファイルを基にテキストファイルのパスを取得
        first_excel_filepath = self._excel_file_set[0].filepath
        output_filepath = first_excel_filepath.with_suffix(".txt")

        # 上書き時の処理
        if output_filepath.exists():
            if overwrite_confirm is None:
                return None
            if not overwrite_confirm(output_filepath):
                return None  # 上書きキャンセル時は処理を中止

        try:
            output_lines = self._material.format_lines
            result = write_text_file(output_filepath, output_lines)
            message = "テキストファイルに変換しました:\n" + str(result)
            self.on_success(OperationType.CONVERT_TO_TEXT, output_filepath, message)
            return result
        except Exception as e:
            self.on_error(OperationType.CONVERT_TO_TEXT, output_filepath, e)
            raise

    def clear_files(self) -> None:
        """追加されたExcelファイル一覧をクリア"""
        self._excel_file_set.clear()
        self.excelFileSetChanged.emit(self._excel_file_set)  # 変更通知
        self._material = None
        self.materialChanged.emit(self._material)  # 変更通知

    def _create_material(self, excel_file_set: ExcelFileSet) -> Material | None:
        """Excelファイルセットを基に `Material` オブジェクトを生成"""
        if not self._excel_file_set:
            return None
        return Material(excel_file_set)

    @property
    def excel_files(self) -> list[ExcelFile]:
        """Excelファイルリスト"""
        return list(self._excel_file_set)

    @property
    def material(self) -> Material | None:
        """材片情報"""
        return self._material


class OperationType(Enum):
    """処理の種別"""

    ADD_FILE = auto()
    REMOVE_FILE = auto()
    CONVERT_TO_TEXT = auto()
