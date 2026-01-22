from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QSettings, QSize
from PySide6.QtWidgets import QMainWindow, QSplitter

INI_FILENAME = "matecon.ini"
DEFAULT_WINDOW_SIZE = QSize(680, 420)


class WindowSettings(QSettings):
    """ウィンドウ設定クラス"""

    def __init__(self, filename=INI_FILENAME):
        # 実行環境に合わせて保存パスを決定
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).parent
        else:
            # app_dir = Path(__file__).parent.resolve()
            app_dir = Path(__file__).parents[1].resolve()

        settings_path = str(app_dir / filename)

        # 親クラス QSettings の初期化（INI形式を指定）
        super().__init__(settings_path, QSettings.Format.IniFormat)

    def save_window_state(self, window: QMainWindow) -> None:
        """ウィンドウの配置と状態を保存する"""
        self.setValue("window/geometry", window.saveGeometry())
        self.setValue("window/windowState", window.saveState())

        self.sync()  # INIファイルに保存

    def restore_window_state(self, window: QMainWindow) -> None:
        """ウィンドウの配置と状態を復元する"""
        geometry = self.value("window/geometry")
        if geometry:
            window.restoreGeometry(geometry)
        else:
            # デフォルトサイズを使用
            window.resize(DEFAULT_WINDOW_SIZE)

        window_state = self.value("window/windowState")
        if window_state:
            window.restoreState(window_state)

    def save_splitter_state(self, splitter: QSplitter):
        """スプリッターの幅リストを保存する"""
        splitter_sizes = splitter.sizes()
        self.setValue("window/splitter", splitter_sizes)

        self.sync()  # INIファイルに保存

    def restore_splitter_state(self, splitter: QSplitter):
        """スプリッターの幅リストを復元する"""
        splitter_sizes = self.value("window/splitter")
        if splitter_sizes:
            # QSettingsから読み出した値（文字列リスト等）を int のリストに変換
            splitter.setSizes([int(s) for s in splitter_sizes])

    def save_last_dir(self, last_dir: str) -> None:
        """最後に開いたディレクトリを保存する"""
        self.setValue("window/last_dir", last_dir)

        self.sync()  # INIファイルに保存

    def get_last_dir(self) -> str:
        """最後に開いたディレクトリを取得"""
        last_dir: str = self.value("windows/last_dir")

        if Path(last_dir).exists():
            return last_dir
        return str(Path.home())
