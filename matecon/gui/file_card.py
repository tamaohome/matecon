from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from matecon.gui.widgets.elided_label import ElidedLabel
from matecon.models.excel_file import ExcelFile
from matecon.models.excel_file_set import ExcelFileSet


class FileCard(QFrame):
    """ファイル情報を表示するカードコンポーネント"""

    excelFileRemoveRequested = Signal(ExcelFile)  # filepathを渡すシグナル

    def __init__(self, excel_file: ExcelFile, parent: QWidget | None = None):
        super().__init__(parent)
        self._excel_file = excel_file
        self._init_ui()

    def _init_ui(self):
        """UIの初期化"""
        # レイアウト
        base_layout = QHBoxLayout(self)
        label_layout = QVBoxLayout()
        base_layout.addLayout(label_layout)

        # ファイル名
        txt_filename = self.filepath.name
        label_filename = ElidedLabel(txt_filename, self)
        label_filename.setObjectName("nameLabel")
        label_layout.addWidget(label_filename)

        # ファイルパス（省略記号対応）
        txt_filepath = str(self.filepath.absolute())
        label_filepath = ElidedLabel(txt_filepath, self)
        label_filepath.setObjectName("pathLabel")
        label_layout.addWidget(label_filepath)

        # シート名一覧
        sheet_label_container = SheetLabelContainer(self)
        sheet_label_container.setObjectName("sheetLabelContainer")
        label_layout.addWidget(sheet_label_container)

        # 削除ボタン
        btn_remove = QPushButton()
        icon_close = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        btn_remove.setIcon(icon_close)
        btn_remove.setObjectName("removeButton")
        btn_remove.clicked.connect(self._on_remove_clicked)
        btn_remove.setFixedSize(QSize(24, 24))
        base_layout.addWidget(btn_remove)

    def _on_remove_clicked(self):
        self.excelFileRemoveRequested.emit(self._excel_file)

    @property
    def filepath(self) -> Path:
        return self._excel_file.filepath

    @property
    def valid_sheet_names(self) -> list[str]:
        """有効なExcelシート一覧"""
        return self._excel_file.valid_sheet_names


class FileCardContainer(QScrollArea):
    """ファイルカードコンテナ"""

    fileCardRemoveRequested = Signal(Path)  # filepathを渡すシグナル

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: list[FileCard] = []
        self._init_ui()

    def _init_ui(self) -> None:
        """レイアウトを作成"""
        self.setWidgetResizable(True)
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self._layout)

        # ドラッグヒントラベル
        self._hint_label = QLabel("ここに Excel ファイルをドラッグ")
        self._hint_label.setObjectName("hintLabel")
        self._hint_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._hint_label)

        self._apply_styles()

    def reload(self, excel_file_set: ExcelFileSet) -> None:
        """ファイルカードを更新する"""
        self._clear_cards()  # 表示済みのカードをクリア
        self._add_cards(excel_file_set)

        # ファイルが存在しない場合のみヒントラベルを表示
        self._hint_label.setVisible(self.is_empty())

    def _add_cards(self, excel_file_set: ExcelFileSet) -> None:
        """ファイルカードウィジェットを追加する"""
        for excel_file in excel_file_set:
            card = FileCard(excel_file, self)
            card.excelFileRemoveRequested.connect(self.fileCardRemoveRequested.emit)
            self._cards.append(card)
            self._layout.addWidget(card)

    def _clear_cards(self):
        """ファイルカードリストを消去"""
        while self.count():
            card = self._cards.pop(0)
            card.deleteLater()

    def is_empty(self) -> bool:
        """ファイルカードが存在しない場合は True を返す"""
        return self.count() == 0

    def count(self) -> int:
        """ファイルカード数を取得"""
        return len(self.cards)

    def _apply_styles(self):
        """スタイルシートを適用"""
        self.setStyleSheet(_FILE_CARD_STYLESHEET)

    @property
    def cards(self) -> tuple[FileCard, ...]:
        return tuple(self._cards)


class SheetLabelContainer(QWidget):
    """Excelシート名一覧を表示するコンテナ"""

    def __init__(self, parent: FileCard):
        super().__init__(parent)
        self._file_card = parent
        self._sheet_names = self._file_card.valid_sheet_names
        self._init_ui()

    def _init_ui(self) -> None:
        """レイアウトを初期化し、シート名バッジを作成する"""
        self._label_layout = QHBoxLayout(self)
        self._label_layout.setContentsMargins(0, 0, 0, 0)
        self._label_layout.setSpacing(6)
        self._add_sheet_labels()
        self._label_layout.addStretch()
        self._apply_styles()

    def _add_sheet_labels(self) -> None:
        """Excelシートラベルを全て追加"""
        for sheet_name in self._sheet_names:
            self._add_sheet_label(sheet_name)

    def _apply_styles(self):
        """スタイルシートを適用"""
        self.setStyleSheet(_SHEET_LABEL_STYLESHEET)

    def _add_sheet_label(self, sheet_name: str) -> None:
        """Excelシートラベルを追加"""
        sheet_label = ElidedLabel(sheet_name, self)
        sheet_label.setObjectName("sheetName")
        self._label_layout.addWidget(sheet_label)


_FILE_CARD_STYLESHEET = """
FileCard {
    border: 1px solid rgba(0, 0, 0, 0.20);
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.85);
    padding: 4px;
}

FileCard:hover {
    border: 1px solid #bbb;
    background-color: #f5f5f5;
}

FileCard QLabel {
    color: #333;
}

FileCard #nameLabel {
    font-weight: bold;
    font-size: 11pt;
    color: #1a1a1a;
}

FileCard #pathLabel {
    font-weight: normal;
    font-size: 9pt;
    color: #666;
}

FileCard #removeButton {
    border: none;
    background: transparent;
}

FileCardContainer #hintLabel {
    font-weight: normal;
    color: #666;
    margin: 8px;
    border: 1px dashed #666;
    border-radius: 8px;
}
"""


_SHEET_LABEL_STYLESHEET = """
#sheetName {
    color: rgba(0, 0, 0, 0.65);
    background-color: rgba(255, 255, 255, 0.50);
    border: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 8px;
    padding: 2px 8px;
    margin: 0;
}
"""
