from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QWidget

# 設定ファイル
INI_FILE = Path.cwd() / "matecon.ini"
INI_FILE_ENCODING = "shift-jis"


@dataclass
class WindowGeometry:
    """ウィンドウ位置およびサイズを保持するクラス"""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        """x, y の範囲を制限"""
        self.x = max(0, self.x)
        self.y = max(0, self.y)

    @staticmethod
    def default() -> WindowGeometry:
        """デフォルト値を返す"""
        return WindowGeometry(100, 100, 680, 420)

    @staticmethod
    def from_qwidget(qwidget: QWidget) -> WindowGeometry:
        """`QWidget` インスタンスより `WindowGeometry` を取得する"""
        g = qwidget.geometry()
        return WindowGeometry(g.x(), g.y(), g.width(), g.height())

    def to_qrect(self) -> QRect:
        """`QRect` 型に変換する"""
        return QRect(self.x, self.y, self.width, self.height)


class ConfigManager:
    """GUI 設定を管理するクラス"""

    def __init__(self, widget: QWidget, ini_file: Path = INI_FILE):
        self._widget = widget
        self.ini_file = ini_file
        self.config = configparser.ConfigParser()
        self._load()

    def _load(self):
        """設定ファイルを読み込む"""
        if self.ini_file.exists():
            self.config.read(self.ini_file, encoding=INI_FILE_ENCODING)

    def save(self):
        """設定ファイルに保存"""
        geometry = WindowGeometry.from_qwidget(self._widget)
        self._set_window_geometry(geometry)
        self.ini_file.parent.mkdir(parents=True, exist_ok=True)
        with self.ini_file.open("w", encoding=INI_FILE_ENCODING) as f:
            self.config.write(f)

    def get_window_geometry(self) -> WindowGeometry:
        """ウィンドウのジオメトリ (x, y, width, height) を取得"""
        if not self.config.has_section("window"):
            return WindowGeometry.default()
        x = self.config.getint("window", "x", fallback=WindowGeometry.default().x)
        y = self.config.getint("window", "y", fallback=WindowGeometry.default().y)
        width = self.config.getint("window", "width", fallback=WindowGeometry.default().width)
        height = self.config.getint("window", "height", fallback=WindowGeometry.default().height)
        return WindowGeometry(x, y, width, height)

    def _set_window_geometry(self, geometry: WindowGeometry):
        """ウィンドウのジオメトリ (x, y, width, height) を保存"""
        if not self.config.has_section("window"):
            self.config.add_section("window")
        self.config.set("window", "x", str(geometry.x))
        self.config.set("window", "y", str(geometry.y))
        self.config.set("window", "width", str(geometry.width))
        self.config.set("window", "height", str(geometry.height))

    def get_last_directory(self) -> str:
        """最後に開いたディレクトリを取得"""
        if not self.config.has_section("paths"):
            return str(Path.home())
        return self.config.get("paths", "last_directory", fallback=str(Path.home()))

    def set_last_directory(self, directory: str):
        """最後に開いたディレクトリを保存"""
        if not self.config.has_section("paths"):
            self.config.add_section("paths")
        self.config.set("paths", "last_directory", directory)

    def get_splitter_sizes(self) -> list[int] | None:
        """スプリッターのサイズを取得"""
        if not self.config.has_section("splitter"):
            return None
        sizes_str = self.config.get("splitter", "sizes", fallback="")
        if not sizes_str:
            return None
        try:
            return [int(s.strip()) for s in sizes_str.split(",") if s.strip()]
        except ValueError:
            return None

    def set_splitter_sizes(self, sizes: list[int]):
        """スプリッターのサイズを保存"""
        if not self.config.has_section("splitter"):
            self.config.add_section("splitter")
        sizes_str = ",".join(str(s) for s in sizes)
        self.config.set("splitter", "sizes", sizes_str)
