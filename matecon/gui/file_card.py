from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from matecon.gui.widgets.elided_label import ElidedLabel


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


class FileCard(QFrame):
    """ファイル情報を表示するカードコンポーネント"""

    def __init__(self, file_path: Path, parent=None):
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
    """ファイルカードコンテナ"""

    def __init__(self, parent=None):
        """コンテナを初期化"""
        super().__init__(parent)
        self._cards: list[FileCard] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """レイアウトを作成"""
        self.setWidgetResizable(True)

        self._base_widget = QWidget()  # QScrollAreaの子要素にはQWidgetが必要
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._base_widget.setLayout(self._layout)
        self.setWidget(self._base_widget)
        self._apply_styles()

    def reload_cards(self, filepaths: list[Path]) -> None:
        """ファイルカードを更新する"""
        self.clear_cards()  # 表示済みのカードをクリア
        for filepath in filepaths:
            card = FileCard(filepath)
            self._cards.append(card)
            self._layout.addWidget(card)

    def clear_cards(self):
        """カードを消去"""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        self._cards.clear()

    def is_empty(self) -> bool:
        """ファイルカードが存在しない場合は True を返す"""
        return len(self.cards) == 0

    def count(self) -> int:
        """ファイルカード数を取得"""
        return len(self.cards)

    def _apply_styles(self):
        """スタイルシートを適用"""
        qss = load_stylesheet("file_card.qss")
        self.setStyleSheet(qss)

    @property
    def cards(self) -> list[FileCard]:
        return list(self._cards)
