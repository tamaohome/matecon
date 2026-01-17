from __future__ import annotations

from pathlib import Path
from typing import override

from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from matecon.gui.config import ConfigManager, WindowGeometry
from matecon.gui.controller import Controller, OperationType
from matecon.gui.file_card import FileCardContainer
from matecon.gui.toolbar import MainToolBar


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.controller = Controller(
            parent=self,
            on_success=self._on_success,
            on_error=self._on_error,
        )

        self.setWindowTitle("まてコン")

        # 保存されたウィンドウ設定を復元
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(geometry.to_qrect())

        # ツールバー
        self.toolbar = MainToolBar(self)
        self.toolbar.addFileTriggered.connect(self.dialog_open_file)
        self.toolbar.convertTriggered.connect(self.dialog_convert)
        self.addToolBar(self.toolbar)

        # メインレイアウト
        central_widget = QWidget()
        self.v_layout = QVBoxLayout()
        self.v_layout.setSpacing(12)
        self.v_layout.setContentsMargins(16, 16, 16, 16)
        central_widget.setLayout(self.v_layout)
        self.setCentralWidget(central_widget)

        # ファイルカードコンテナ
        self.card_container = FileCardContainer()
        self.v_layout.addWidget(self.card_container)

        self.setAcceptDrops(True)  # ドロップ受付を有効化

        self.controller.excelFilesChanged.connect(self._on_excel_files_changed)

    @override
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    @override
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            self.controller.add_excel_file(filepath)

    def _on_success(self, op_type: OperationType, path, message):
        """オペレーション成功時の処理"""
        self._set_processing_state(False)
        QMessageBox.information(self, "成功", message)

    def _on_error(self, op_type: OperationType, path, exception):
        """オペレーション失敗時の処理"""
        self._set_processing_state(False)
        QMessageBox.critical(self, "エラー", str(exception))

    def _on_excel_files_changed(self, filepaths: list):
        """Excelファイルリスト変更時のスロット"""
        self.card_container.reload_cards(filepaths)
        self._set_processing_state(False)

    def _set_processing_state(self, is_processing: bool) -> None:
        """処理中/待機中の状態を設定"""
        self.toolbar.action_open.setEnabled(not is_processing)
        self.toolbar.action_convert.setEnabled(not is_processing and self.card_container.count() > 0)

    def dialog_open_file(self) -> None:
        """ファイル追加ダイアログを表示"""
        filter_str = "Excel Files (*.xlsx *.xlsm)"
        last_dir = self.config_manager.get_last_directory()
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Excelファイルを選択", last_dir, filter_str)
        if not filepaths:
            return

        # ディレクトリを保存
        parent_dir = str(Path(filepaths[0]).parent)
        self.config_manager.set_last_directory(parent_dir)
        self.config_manager.save()

        # ファイルを追加
        self.controller.add_excel_files([Path(fp) for fp in filepaths])

    def dialog_convert(self):
        """テキストファイル変換ダイアログを表示"""
        print("convert(): 実行")
        print("現在のファイルパス:", self.controller.excel_files)

        def overwrite_confirm(path: Path) -> bool:
            reply = QMessageBox.question(
                self,
                "上書き確認",
                f"既にファイルが存在します。\n上書きしますか？\n\n{path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            return reply == QMessageBox.StandardButton.Yes

        self.controller.convert_to_text_file(overwrite_confirm=overwrite_confirm)

    @override
    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        geometry = WindowGeometry.from_qwidget(self)
        self.config_manager.set_window_geometry(geometry)
        self.config_manager.save()
        event.accept()
