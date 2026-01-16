from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar


class MainToolBar(QToolBar):
    """メインツールバークラス"""

    # シグナル定義
    open_file_triggered = Signal()
    convert_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self.setIconSize(self.iconSize())
        self._setup_actions()

    def _setup_actions(self):
        """ツールバーアクションを設定"""
        # ファイルを開く
        self.action_open = QAction("ファイルを開く", self)
        self.action_open.setShortcut("Ctrl+O")
        self.action_open.triggered.connect(self.open_file_triggered.emit)
        self.addAction(self.action_open)

        # 変換
        self.action_convert = QAction("TXTに変換", self)
        self.action_convert.setShortcut("Ctrl+E")
        self.action_convert.setEnabled(False)  # 初期状態は無効
        self.action_convert.triggered.connect(self.convert_triggered.emit)
        self.addAction(self.action_convert)
