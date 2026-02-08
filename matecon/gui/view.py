from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import override

from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
)

from matecon.gui.controller import Controller, OperationType
from matecon.gui.file_card import FileCardContainer
from matecon.gui.material_treeview import MaterialTreeView
from matecon.gui.settings import WindowSettings
from matecon.gui.toolbar import MainToolBar
from matecon.models.excel_file_set import ExcelFileSet
from matecon.models.material import Material


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self, initial_filepaths: Sequence[Path] | None = None):
        super().__init__()
        self.settings = WindowSettings()  # ウィンドウ設定
        self.controller = Controller(parent=self, on_success=self._on_success, on_error=self._on_error)

        self.setWindowTitle("まてコン")

        # ツールバー
        self.toolbar = MainToolBar(self)
        self.toolbar.fileAddRequested.connect(self.dialog_open_file)
        self.toolbar.convertRequested.connect(self.dialog_convert)
        self.toolbar.clearRequested.connect(self.dialog_clear)
        self.addToolBar(self.toolbar)

        # メインレイアウト
        self.splitter = QSplitter()
        self.setCentralWidget(self.splitter)

        # ファイルカードコンテナ
        self.card_container = FileCardContainer()
        self.card_container.fileCardRemoveRequested.connect(self._on_card_remove_requested)
        self.splitter.addWidget(self.card_container)
        self.splitter.setStretchFactor(0, 0)  # ファイルカードの幅を固定

        # ツリービュー
        self.material_tree = MaterialTreeView()
        self.splitter.addWidget(self.material_tree)
        self.splitter.setStretchFactor(1, 1)  # ツリービューの幅をストレッチ

        # シグナルとスロットを接続
        self.controller.excelFileSetChanged.connect(self._on_excel_file_set_changed)
        self.controller.materialChanged.connect(self._on_material_changed)

        # 保存されたウィンドウ設定を復元
        self.restore_window_settings()

        self.setAcceptDrops(True)  # ドロップ受付を有効化

        # コマンドライン引数からファイルパスを取得
        if initial_filepaths:
            self.controller.add_excel_files(initial_filepaths)

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

    def _on_excel_file_set_changed(self, excel_file_set: ExcelFileSet):
        """Excelファイルセット変更時のスロット"""
        self.card_container.reload(excel_file_set)  # カードリストを更新

        # ツールバーのボタン状態を更新
        self.toolbar.set_convert_enabled(len(excel_file_set) > 0)
        self.toolbar.set_clear_enabled(len(excel_file_set) > 0)

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
        try:
            self.controller.add_excel_files(filepaths)
        except Exception as e:
            # ExcelFile 生成時のエラーを on_error に委譲
            self.controller.on_error(OperationType.ADD_FILE, Path(filepaths[0] if filepaths else ""), e)

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

        # 保存先ファイル名をユーザに選ばせるダイアログを表示
        default_filepath = ""
        if self.controller.excel_files:
            try:
                default_filepath = str(self.controller.excel_files[0].filepath.with_suffix(".txt"))
            except Exception:
                default_filepath = ""

        output_filepath_str, _ = QFileDialog.getSaveFileName(
            self, "保存先を選択", default_filepath, "Text Files (*.txt)"
        )
        if not output_filepath_str:
            return  # キャンセルされた場合は処理中止

        output_path = Path(output_filepath_str)
        self.controller.convert_to_text_file(overwrite_confirm=overwrite_confirm, output_filepath=output_path)

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
