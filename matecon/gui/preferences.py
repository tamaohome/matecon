from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSettings, Signal
from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QVBoxLayout, QWidget

from matecon.gui.settings import INI_FILENAME, get_ini_path

KEY_TIMESTAMP_SUFFIX = "preferences/timestamp_suffix"
DEFAULT_TIMESTAMP_SUFFIX = False
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


def with_timestamp_suffix(path: Path, now: datetime | None = None) -> Path:
    """ファイル名の末尾（拡張子の直前）に日時のサフィックスを付与したパスを返す"""
    now = now or datetime.now()
    return path.with_name(f"{path.stem}_{now.strftime(TIMESTAMP_FORMAT)}{path.suffix}")


class PreferencesSettings(QSettings):
    """環境設定クラス（ウィンドウ設定と同じ INI ファイルに保存する）"""

    def __init__(self, filename: str = INI_FILENAME):
        super().__init__(get_ini_path(filename), QSettings.Format.IniFormat)

    def is_timestamp_suffix_enabled(self) -> bool:
        """日時のサフィックスを付与するかどうかを取得する"""
        return bool(self.value(KEY_TIMESTAMP_SUFFIX, DEFAULT_TIMESTAMP_SUFFIX, type=bool))

    def set_timestamp_suffix_enabled(self, enabled: bool) -> None:
        """日時のサフィックスを付与するかどうかを保存する"""
        self.setValue(KEY_TIMESTAMP_SUFFIX, enabled)

        self.sync()  # INIファイルに保存


class PreferencesDialog(QDialog):
    """環境設定ダイアログクラス"""

    preferencesSaved = Signal()

    def __init__(self, settings: PreferencesSettings, parent: QWidget | None = None):
        super().__init__(parent)
        self._settings = settings

        self.setWindowTitle("環境設定")

        self._setup_ui()
        self._connect_signals()
        self._load_values()

    def _setup_ui(self) -> None:
        """ダイアログのレイアウトを構築する"""
        self._chk_timestamp_suffix = QCheckBox("保存時のファイル名に日時のサフィックスを付与する")

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self._chk_timestamp_suffix)
        layout.addWidget(self._button_box)

    def _connect_signals(self) -> None:
        """シグナルとスロットを接続する"""
        self._button_box.accepted.connect(self._on_accepted)
        self._button_box.rejected.connect(self.reject)

    def _load_values(self) -> None:
        """保存済みの設定値をウィジェットに反映する"""
        self._chk_timestamp_suffix.setChecked(self._settings.is_timestamp_suffix_enabled())

    def _on_accepted(self) -> None:
        """OK 押下時に設定を保存して閉じる"""
        self._settings.set_timestamp_suffix_enabled(self._chk_timestamp_suffix.isChecked())
        self.preferencesSaved.emit()
        self.accept()
