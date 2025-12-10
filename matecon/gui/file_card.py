from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def load_stylesheet(filename: str) -> str:
    """スタイルシート (`*.qss`) を読み込む"""
    qss_path = Path(__file__).parent / filename
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


class FileCard(QFrame):
    """ファイル選択状態を表示するカードコンポーネント"""

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self._init_ui()
        self._apply_styles()

    def _init_ui(self):
        """UIの初期化"""
        layout = QVBoxLayout()

        # ファイル名
        file_name = Path(self.file_path).name
        self.name_label = QLabel(file_name)
        self.name_label.setObjectName("nameLabel")
        layout.addWidget(self.name_label)

        layout.addStretch()
        self.setLayout(layout)

    def _apply_styles(self):
        """スタイルシートを適用"""
        qss = load_stylesheet("file_card.qss")
        self.setStyleSheet(qss)


class FileCardContainer:
    """
    ファイルカードコンテナ

    - カードのライフサイクルと UI を管理
    """

    def __init__(self):
        """コンテナを初期化"""
        self._cards: dict[str, FileCard] = {}
        self._create_ui()

    def _create_ui(self) -> None:
        """スクロールエリアとレイアウトを作成"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container_widget = QWidget()
        self.layout = QVBoxLayout()
        self.container_widget.setLayout(self.layout)
        self.scroll_area.setWidget(self.container_widget)

    def get_scroll_area(self) -> QScrollArea:
        """スクロールエリア UI を取得"""
        return self.scroll_area

    def add_card(self, file_path: str) -> FileCard | None:
        """ファイルカードを追加"""
        if file_path in self._cards:
            return None

        card = FileCard(file_path)
        self._cards[file_path] = card
        self.layout.insertWidget(len(self._cards) - 1, card)
        return card

    def get_card(self, file_path: str) -> FileCard | None:
        """ファイルパスに対応するカードを取得"""
        return self._cards.get(file_path)

    def remove_card(self, file_path: str) -> None:
        """ファイルカードを削除"""
        if file_path not in self._cards:
            return

        card = self._cards[file_path]
        self.layout.removeWidget(card)
        card.deleteLater()
        del self._cards[file_path]

    def clear(self) -> None:
        """すべてのファイルカードを削除"""
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
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
