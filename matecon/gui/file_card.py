from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QScrollArea, QStyle, QVBoxLayout, QWidget

from matecon.gui.utils import load_stylesheet
from matecon.gui.widgets.elided_label import ElidedLabel


class FileCard(QFrame):
    """ファイル情報を表示するカードコンポーネント"""

    fileRemoveRequested = Signal(Path)  # filepathを渡すシグナル

    def __init__(self, filepath: Path, parent: QWidget | None = None):
        super().__init__(parent)
        self._filepath = filepath
        self._init_ui()

    def _init_ui(self):
        """UIの初期化"""
        # レイアウト
        h_layout = QHBoxLayout()
        label_container = QVBoxLayout()
        h_layout.addLayout(label_container)
        label_container.addStretch()
        self.setLayout(h_layout)

        # ファイル名
        txt_filename = Path(self._filepath).name
        label_filename = ElidedLabel(txt_filename)
        label_filename.setObjectName("nameLabel")
        label_container.addWidget(label_filename)

        # ファイルパス（省略記号対応）
        txt_filepath = Path(self._filepath).parent.as_posix() + os.sep  # 末尾はパス区切り文字
        label_filepath = ElidedLabel(txt_filepath)
        label_filepath.setObjectName("pathLabel")
        label_container.addWidget(label_filepath)

        # 削除ボタン
        btn_remove = QPushButton()
        icon_close = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        btn_remove.setIcon(icon_close)
        btn_remove.setObjectName("removeButton")
        btn_remove.clicked.connect(self._on_remove_clicked)
        btn_remove.setFixedSize(QSize(24, 24))
        h_layout.addWidget(btn_remove)

    def _on_remove_clicked(self):
        self.fileRemoveRequested.emit(self._filepath)


class FileCardContainer(QScrollArea):
    """ファイルカードコンテナ"""

    fileCardRemoveRequested = Signal(Path)  # filepathを渡すシグナル

    def __init__(self, parent=None):
        """コンテナを初期化"""
        super().__init__(parent)
        self._cards: list[FileCard] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """レイアウトを作成"""
        self.setWidgetResizable(True)
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self._layout)
        self._apply_styles()

    def reload_cards(self, filepaths: Sequence[Path]) -> None:
        """ファイルカードを更新する"""
        self.clear_cards()  # 表示済みのカードをクリア
        for filepath in filepaths:
            card = FileCard(filepath, self)
            card.fileRemoveRequested.connect(self.fileCardRemoveRequested.emit)
            self._cards.append(card)
            self._layout.addWidget(card)

    def clear_cards(self):
        """ファイルカードリストを消去"""
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
    def cards(self) -> tuple[FileCard, ...]:
        return tuple(self._cards)
