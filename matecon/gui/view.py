from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import override

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QWidget,
)

from matecon.gui.controller import Controller, OperationType
from matecon.gui.file_card import FileCardContainer
from matecon.gui.material_treeview import MaterialTreeView
from matecon.gui.settings import WindowSettings
from matecon.gui.toolbar import MainToolBar
from matecon.models.material import Material


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()
        self.settings = WindowSettings()  # ウィンドウ設定
        self.controller = Controller(
            parent=self,
            on_success=self._on_success,
            on_error=self._on_error,
        )

        self.setWindowTitle("まてコン")

        # ツールバー
        self.toolbar = MainToolBar(self)
        self.toolbar.fileAddRequested.connect(self.dialog_open_file)
        self.toolbar.convertRequested.connect(self.dialog_convert)
        self.toolbar.clearRequested.connect(self.dialog_clear)
        self.addToolBar(self.toolbar)

        # メインレイアウト
        central_widget = QWidget()
        self.h_layout = QHBoxLayout()
        central_widget.setLayout(self.h_layout)
        self.setCentralWidget(central_widget)
        self.splitter = QSplitter()
        self.h_layout.addWidget(self.splitter)

        # ファイルカードコンテナ
        self.card_container = FileCardContainer()
        self.card_container.fileCardRemoveRequested.connect(self._on_card_remove_requested)
        self.splitter.addWidget(self.card_container)

        # ツリービュー
        self.material_tree = MaterialTreeView()
        self.splitter.addWidget(self.material_tree)

        # シグナルとスロットを接続
        self.controller.excelFilesChanged.connect(self._on_excel_files_changed)
        self.controller.materialChanged.connect(self._on_material_changed)

        # 保存されたウィンドウ設定を復元
        self.restore_window_settings()

        self.setAcceptDrops(True)  # ドロップ受付を有効化

    def save_window_settings(self) -> None:
        """ウィンドウ設定を保存"""
        self.settings.save_window_state(self)
        self.settings.save_splitter_state(self.splitter)

    def restore_window_settings(self) -> None:
        """保存されたウィンドウ設定を復元"""
        self.settings.restore_window_state(self)
        self.settings.restore_splitter_state(self.splitter)

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
        QMessageBox.information(self, "成功", message)

    def _on_error(self, op_type: OperationType, path, exception):
        """オペレーション失敗時の処理"""
        QMessageBox.critical(self, "エラー", str(exception))

    def _on_excel_files_changed(self, filepaths: Sequence[Path]):
        """Excelファイルリスト変更時のスロット"""
        self.card_container.reload(filepaths)  # カードリストを更新

        # ツールバーのボタン状態を更新
        self.toolbar.set_convert_enabled(len(filepaths) > 0)
        self.toolbar.set_clear_enabled(len(filepaths) > 0)

    def _on_material_changed(self, material: Material):
        """`Material` インスタンス変更時のスロット"""
        self.material_tree.reload(material)  # ツリーを更新

    def _on_card_remove_requested(self, filepath):
        """
        カードの削除要求があった際に呼び出されるメソッド

        指定されたファイルパスのExcelファイルを `Controller` から削除する
        """
        self.controller.remove_excel_file(filepath)

    def _on_material_exists(self, exists: bool):
        """`Material` の有無に応じてツリー内容を更新"""
        self.material_tree.reload(self.controller.material if exists else None)

    def dialog_open_file(self) -> None:
        """ファイル追加ダイアログを表示"""
        filter_str = "Excel Files (*.xlsx *.xlsm)"
        last_dir = self.settings.get_last_dir()
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Excelファイルを選択", last_dir, filter_str)
        if not filepaths:
            return

        # ディレクトリを保存
        parent_dir = str(Path(filepaths[0]).parent)
        self.settings.save_last_dir(parent_dir)

        # ファイルを追加
        self.controller.add_excel_files([Path(fp) for fp in filepaths])

    def dialog_convert(self):
        """テキストファイル変換ダイアログを表示"""

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

    def dialog_clear(self):
        """ファイル一覧クリアの確認ダイアログを表示"""
        reply = QMessageBox.question(
            self,
            "ファイル一覧のクリア",
            "Excelファイル一覧をクリアしますか？\n(ファイル自体は削除されません)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.clear_files()

    @override
    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        self.save_window_settings()
        event.accept()
