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
        self.setObjectName("mainToolbar")
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

        self._action_open = QAction("ファイルを開く", self)
        self._action_open.setShortcut("Ctrl+O")
        self._action_open.triggered.connect(self.fileAddRequested.emit)
        icon_open = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        self._action_open.setIcon(icon_open)
        self.addAction(self._action_open)

        self._action_convert = QAction("テキストに変換", self)
        self._action_convert.setShortcut("Ctrl+E")
        self._action_convert.setEnabled(False)  # 初期状態は無効
        self._action_convert.triggered.connect(self.convertRequested.emit)
        icon_save = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        self._action_convert.setIcon(icon_save)
        self.addAction(self._action_convert)

        self._action_clear = QAction("ファイル一覧をクリア", self)
        self._action_clear.setEnabled(False)  # 初期状態は無効
        self._action_clear.triggered.connect(self.clearRequested.emit)
        icon_clear = self.style().standardIcon(QStyle.StandardPixmap.SP_LineEditClearButton)
        self._action_clear.setIcon(icon_clear)
        self.addAction(self._action_clear)

    def set_convert_enabled(self, enabled: bool):
        self._action_convert.setEnabled(enabled)

    def set_clear_enabled(self, enabled: bool):
        self._action_clear.setEnabled(enabled)
