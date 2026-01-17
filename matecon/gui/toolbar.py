from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar


class MainToolBar(QToolBar):
    """メインツールバークラス"""

    # シグナル定義
    addFileTriggered = Signal()
    convertTriggered = Signal()
    clearTriggered = Signal()

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self.setIconSize(self.iconSize())
        self._setup_actions()

    def _setup_actions(self):
        """ツールバーアクションを設定"""
        self.action_open = QAction("ファイルを開く", self)
        self.action_open.setShortcut("Ctrl+O")
        self.action_open.triggered.connect(self.addFileTriggered.emit)
        self.addAction(self.action_open)

        self.action_convert = QAction("テキストに変換", self)
        self.action_convert.setShortcut("Ctrl+E")
        self.action_convert.setEnabled(False)  # 初期状態は無効
        self.action_convert.triggered.connect(self.convertTriggered.emit)
        self.addAction(self.action_convert)

        self.action_clear = QAction("ファイル一覧をクリア", self)
        self.action_clear.setEnabled(False)  # 初期状態は無効
        self.action_clear.triggered.connect(self.clearTriggered.emit)
        self.addAction(self.action_clear)
