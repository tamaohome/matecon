from __future__ import annotations

from collections.abc import Callable

from matecon.io.spreadsheet_reader import validate_excel_filepath
from matecon.models.material import Material
from matecon.utils.io import write_txt


class Controller:
    """
    コントローラクラス

    ユーザ入力を受け取り、モデルを操作する
    """

    def __init__(
        self,
        on_success: Callable[[str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ):
        self.on_success = on_success or (lambda _: None)
        self.on_error = on_error or (lambda _: None)
        self.material: Material | None = None

    def validate_file(self, file_path: str) -> bool:
        """ファイルの妥当性を検証"""
        try:
            validate_excel_filepath(file_path)
            return True
        except (FileNotFoundError, ValueError, OSError):
            return False

    def convert_file(self, file_path: str) -> str | None:
        """Excel ファイルを JIP-MATERIAL テキストに変換"""
        try:
            if not self.validate_file(file_path):
                error_msg = f"無効な Excel ファイルです: {file_path}"
                self.on_error(error_msg)
                raise ValueError(error_msg)

            # Material から材料データを読み込む
            self.material = Material(file_path)

            # テキストファイルを出力
            txt_path = write_txt(file_path, self.material.format_lines)

            # リソースを解放
            self.cleanup()

            # 成功コールバック
            self.on_success(str(txt_path))
            return str(txt_path)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            self.on_error(error_msg)
            self.cleanup()
            raise

    def cleanup(self):
        """`Material` をクリーンアップ"""
        if self.material is not None:
            self.material.cleanup()
            self.material = None
