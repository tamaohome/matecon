from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QStyle, QToolBar


class MainToolBar(QToolBar):
    """メインツールバークラス"""

    # シグナル定義
    fileAddRequested = Signal()
    convertRequested = Signal()
    clearRequested = Signal()

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self.setIconSize(self.iconSize())
        self._setup_actions()

    def _setup_actions(self):
        """ツールバーアクションを設定"""

        # アイコンの横にラベルを表示
        self.setToolButtonStyle(self.toolButtonStyle().ToolButtonTextBesideIcon)
        # デフォルトのアイコンサイズを設定
        default_icon_size = QSize(16, 16)
        self.setIconSize(default_icon_size)

        self.action_open = QAction("ファイルを開く", self)
        self.action_open.setShortcut("Ctrl+O")
        self.action_open.triggered.connect(self.fileAddRequested.emit)
        icon_open = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        self.action_open.setIcon(icon_open)
        self.addAction(self.action_open)

        self.action_convert = QAction("テキストに変換", self)
        self.action_convert.setShortcut("Ctrl+E")
        self.action_convert.setEnabled(False)  # 初期状態は無効
        self.action_convert.triggered.connect(self.convertRequested.emit)
        icon_save = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        self.action_convert.setIcon(icon_save)
        self.addAction(self.action_convert)

        self.action_clear = QAction("ファイル一覧をクリア", self)
        self.action_clear.setEnabled(False)  # 初期状態は無効
        self.action_clear.triggered.connect(self.clearRequested.emit)
        icon_clear = self.style().standardIcon(QStyle.StandardPixmap.SP_LineEditClearButton)
        self.action_clear.setIcon(icon_clear)
        self.addAction(self.action_clear)
