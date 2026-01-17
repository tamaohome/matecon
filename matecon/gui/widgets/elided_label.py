from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QLabel,
)


class ElidedLabel(QLabel):
    """省略記号を自動表示するラベルウィジェット"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self._full_text = text
        super().setText(text)

    def setText(self, text: str) -> None:
        """テキストを設定し、必要に応じて省略"""
        self._full_text = text
        self._update_elided_text()

    def _update_elided_text(self) -> None:
        """ウィジェットの幅に合わせてテキストを省略"""
        font_metrics = QFontMetrics(self.font())
        elided_text = font_metrics.elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            self.width() - 4,  # パディングを考慮
        )
        super().setText(elided_text)

    def resizeEvent(self, event):
        """ウィジェットのサイズが変わったときにテキストを更新"""
        super().resizeEvent(event)
        self._update_elided_text()
