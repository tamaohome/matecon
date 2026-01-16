from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def load_stylesheet(filename: str) -> str:
    """スタイルシート (`*.qss`) を読み込む"""
    # PyInstaller での実行環境に対応
    if getattr(sys, "frozen", False):
        # exe 実行時
        qss_path = Path(getattr(sys, "_MEIPASS", ".")) / "matecon" / "gui" / filename
    else:
        # 開発環境
        qss_path = Path(__file__).parent / filename

    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


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


class FileCard(QFrame):
    """ファイル選択状態を表示するカードコンポーネント"""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self._file_path = file_path
        self._init_ui()

    def _init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout()

        # ファイル名
        txt_filename = Path(self._file_path).name
        self._label_filename = ElidedLabel(txt_filename)
        self._label_filename.setObjectName("nameLabel")
        layout.addWidget(self._label_filename)

        # ファイルパス（省略記号対応）
        txt_filepath = Path(self._file_path).as_posix()
        self._label_filepath = ElidedLabel(txt_filepath)
        self._label_filepath.setObjectName("pathLabel")
        layout.addWidget(self._label_filepath)

        layout.addStretch()
        self.setLayout(layout)


class FileCardContainer(QScrollArea):
    """
    ファイルカードコンテナ

    - カードのライフサイクルと UI を管理
    """

    def __init__(self, parent=None):
        """コンテナを初期化"""
        super().__init__(parent)
        self._cards: dict[str, FileCard] = {}
        self._init_ui()
        self._apply_styles()

    def _init_ui(self) -> None:
        """レイアウトを作成"""
        self.setWidgetResizable(True)

        self._container_widget = QWidget()  # QScrollAreaの子要素にはQWidgetが必要
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._container_widget.setLayout(self._layout)
        self.setWidget(self._container_widget)

    def add_card(self, file_path: str) -> FileCard | None:
        """ファイルカードを追加"""
        if file_path in self._cards:
            return None

        card = FileCard(file_path)
        self._cards[file_path] = card
        self._layout.addWidget(card)
        return card

    def get_card(self, file_path: str) -> FileCard | None:
        """ファイルパスに対応するカードを取得"""
        return self._cards.get(file_path)

    def remove_card(self, file_path: str) -> None:
        """ファイルカードを削除"""
        if file_path not in self._cards:
            return

        card = self._cards[file_path]
        self._layout.removeWidget(card)
        card.deleteLater()
        del self._cards[file_path]

    def clear(self) -> None:
        """すべてのファイルカードを削除"""
        while self._layout.count():
            widget = self._layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self._cards.clear()

    def is_empty(self) -> bool:
        """ファイルカードが存在しない場合は True を返す"""
        return len(self._cards) == 0

    def get_file_paths(self) -> list[str]:
        """すべてのファイルパスを取得"""
        return list(self._cards.keys())

    def count(self) -> int:
        """ファイルカード数を取得"""
        return len(self._cards)

    def _apply_styles(self):
        """スタイルシートを適用"""
        qss = load_stylesheet("file_card.qss")
        self.setStyleSheet(qss)
