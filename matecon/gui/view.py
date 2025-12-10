from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matecon.gui.config import ConfigManager, WindowGeometry
from matecon.gui.controller import Controller
from matecon.gui.file_card import FileCardContainer


class ConversionWorker(QThread):
    """ファイル変換処理をバックグラウンドで実行"""

    finished = Signal(str)  # 成功時
    error = Signal(str)  # エラー時

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.controller = Controller(on_success=self.finished.emit, on_error=self.error.emit)

    def run(self):
        try:
            self.controller.convert_file(self.file_path)
        finally:
            self.controller.cleanup()


class MainWindow(QWidget):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.controller = Controller()

        self.setWindowTitle("まてコン")

        # 保存されたウィンドウ設定を復元
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(geometry.to_qrect())

        # メインレイアウト
        self.v_layout = QVBoxLayout()
        self.v_layout.setSpacing(12)
        self.v_layout.setContentsMargins(16, 16, 16, 16)

        # ボタンエリア
        button_layout = QHBoxLayout()
        self.button_select = QPushButton("ファイル選択")
        self.button_select.clicked.connect(self.select_file)
        self.button_convert = QPushButton("変換")
        self.button_convert.clicked.connect(self.convert_file)
        self.button_convert.setEnabled(False)
        button_layout.addWidget(self.button_select)
        button_layout.addWidget(self.button_convert)
        button_layout.addStretch()
        self.v_layout.addLayout(button_layout)

        # ファイルカードコンテナ
        self.card_container = FileCardContainer()
        self.v_layout.addWidget(self.card_container.get_scroll_area())

        self.setLayout(self.v_layout)

        self.setAcceptDrops(True)  # ドロップ受付を有効化
        self.workers: dict[str, ConversionWorker] = {}

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(
            self.controller.validate_file(url.toLocalFile()) for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not self.controller.validate_file(file_path):
                continue
            self._add_file(file_path)

    def _add_file(self, file_path: str) -> None:
        """ファイルを追加し、カードを作成"""
        card = self.card_container.add_card(file_path)
        if card is not None:
            # 変換ボタンを有効化
            self.button_convert.setEnabled(True)

    def _reset_ui(self) -> None:
        """UIを初期状態にリセット"""
        self.card_container.clear()
        self.button_convert.setEnabled(False)

    def _set_processing_state(self, is_processing: bool) -> None:
        """処理中/待機中の状態を設定"""
        self.button_select.setEnabled(not is_processing)
        self.button_convert.setEnabled(not is_processing and self.card_container.count() > 0)

    def select_file(self):
        filter_str = "Excel Files (*.xlsx *.xlsm)"
        last_dir = self.config_manager.get_last_directory()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Excelファイルを選択", last_dir, filter_str)
        if not file_paths:
            return
        # ディレクトリを保存
        parent_dir = str(Path(file_paths[0]).parent)
        self.config_manager.set_last_directory(parent_dir)
        self.config_manager.save()
        # ファイルを追加
        for file_path in file_paths:
            self._add_file(file_path)

    def convert_file(self):
        if self.card_container.is_empty():
            return
        # すべてのファイルを変換
        for file_path in self.card_container.get_file_paths():
            self.handle_file(file_path)

    def handle_file(self, file_path: str):
        """
        入力ファイルに対するファイル変換をバックグラウンドで実行する

        - 既存の `ConversionWorker` が実行中の場合は終了を待つ
        - 処理完了後は自動的に `ConversionWorker` インスタンスをメモリから解放する
        """
        # 既存の ConversionWorker があれば終了を待つ
        if file_path in self.workers:
            worker = self.workers[file_path]
            try:
                if worker.isRunning():
                    worker.quit()
                    worker.wait()
            except RuntimeError:
                pass

        self._set_processing_state(True)

        worker = ConversionWorker(file_path)
        self.workers[file_path] = worker
        worker.finished.connect(lambda txt_path: self._on_success(file_path, txt_path))
        worker.error.connect(lambda error_msg: self._on_error(file_path, error_msg))
        worker.finished.connect(lambda: self._cleanup_worker(file_path))
        worker.error.connect(lambda: self._cleanup_worker(file_path))
        worker.start()

    def _cleanup_worker(self, file_path: str):
        """ワーカーをクリーンアップ"""
        if file_path in self.workers:
            worker = self.workers[file_path]
            worker.deleteLater()
            del self.workers[file_path]

    def _on_success(self, file_path: str, txt_path: str):
        """変換成功時の処理"""
        self._set_processing_state(False)
        QMessageBox.information(self, "完了", f"{txt_path}\nテキストデータを出力しました。")

    def _on_error(self, file_path: str, error_msg: str):
        """変換エラー時の処理"""
        self._set_processing_state(False)
        QMessageBox.critical(self, "エラー", error_msg)

    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        geometry = WindowGeometry.from_qwidget(self)
        self.config_manager.set_window_geometry(geometry)
        self.config_manager.save()
        event.accept()
