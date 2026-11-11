from __future__ import annotations

from PySide6.QtCore import QSettings

from matecon.gui.settings import INI_FILENAME, get_ini_path

KEY_TIMESTAMP_SUFFIX = "preferences/timestamp_suffix"
DEFAULT_TIMESTAMP_SUFFIX = False


class PreferencesSettings(QSettings):
    """環境設定クラス（ウィンドウ設定と同じ INI ファイルに保存する）"""

    def __init__(self, filename: str = INI_FILENAME, settings_path: str | None = None):
        # settings_path を指定した場合はそのパスを使う（テスト用）
        path = settings_path if settings_path is not None else get_ini_path(filename)
        super().__init__(path, QSettings.Format.IniFormat)

    def is_timestamp_suffix_enabled(self) -> bool:
        """日時のサフィックスを付与するかどうかを取得する"""
        return self.value(KEY_TIMESTAMP_SUFFIX, DEFAULT_TIMESTAMP_SUFFIX, type=bool)

    def set_timestamp_suffix_enabled(self, enabled: bool) -> None:
        """日時のサフィックスを付与するかどうかを保存する"""
        self.setValue(KEY_TIMESTAMP_SUFFIX, enabled)

        self.sync()  # INIファイルに保存
