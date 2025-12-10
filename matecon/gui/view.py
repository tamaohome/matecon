from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matecon.gui.config import ConfigManager, WindowGeometry
from matecon.gui.controller import Controller

# デフォルトラベル
DEFAULT_LABEL_TEXT = "Excelファイルを選択してください\n(またはこのウィンドウにファイルをドロップ)"


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

        self.v_layout = QVBoxLayout()

        self.label = QLabel(DEFAULT_LABEL_TEXT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.button_select = QPushButton("ファイル選択")
        self.button_select.clicked.connect(self.select_file)
        self.button_convert = QPushButton("変換")
        self.button_convert.clicked.connect(self.convert_file)
        self.button_convert.setEnabled(False)

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.button_select)
        self.v_layout.addWidget(self.button_convert)
        self.setLayout(self.v_layout)

        self.setAcceptDrops(True)  # ドロップ受付を有効化
        self.worker: ConversionWorker | None = None
        self.selected_file_path = None

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
            self._set_selected_file(file_path)
            return

    def _set_selected_file(self, file_path: str) -> None:
        """ファイル選択時の共通UI更新処理"""
        self.selected_file_path = file_path
        file_name = Path(file_path).name
        self.label.setText(f"ファイル: {file_name}\n「変換」ボタンを押してください")
        self.button_convert.setEnabled(True)

    def _reset_ui(self) -> None:
        """UIを初期状態にリセット"""
        self.label.setText(DEFAULT_LABEL_TEXT)
        self.selected_file_path = None
        self.button_convert.setEnabled(False)

    def _set_processing_state(self, is_processing: bool) -> None:
        """処理中/待機中の状態を設定"""
        self.button_select.setEnabled(not is_processing)
        self.button_convert.setEnabled(not is_processing and self.selected_file_path is not None)
        if is_processing:
            self.label.setText("処理中...")

    def select_file(self):
        filter_str = "Excel Files (*.xlsx *.xlsm)"
        last_dir = self.config_manager.get_last_directory()
        file_path, _ = QFileDialog.getOpenFileName(self, "Excelファイルを選択", last_dir, filter_str)
        if not file_path:
            return
        # ディレクトリを保存
        parent_dir = str(Path(file_path).parent)
        self.config_manager.set_last_directory(parent_dir)
        self.config_manager.save()
        self._set_selected_file(file_path)

    def convert_file(self):
        if not self.selected_file_path:
            return
        self.handle_file(self.selected_file_path)

    def handle_file(self, file_path: str):
        """
        入力ファイルに対するファイル変換をバックグラウンドで実行する

        - 既存の `ConversionWorker` が実行中の場合は終了を待つ
        - 処理完了後は自動的に `ConversionWorker` インスタンスをメモリから解放する
        """
        # 既存の ConversionWorker があれば終了を待つ
        if self.worker is not None:
            # ConversionWorker の実行状態を確認
            try:
                if self.worker.isRunning():
                    self.worker.quit()
                    self.worker.wait()
            except RuntimeError:
                # ConversionWorker が削除済みの場合はスキップ
                pass

        self._set_processing_state(True)

        self.worker = ConversionWorker(file_path)
        self.worker.finished.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self.worker.deleteLater)  # メモリ解放
        self.worker.error.connect(self.worker.deleteLater)
        self.worker.start()

    def _on_success(self, txt_path: str):
        self._set_processing_state(False)
        self._reset_ui()
        QMessageBox.information(self, "完了", f"{txt_path}\nテキストデータを出力しました。")

    def _on_error(self, error_msg: str):
        self._set_processing_state(False)
        if self.selected_file_path:
            file_name = Path(self.selected_file_path).name
            self.label.setText(f"ファイル: {file_name}\n「変換」ボタンを押してください")
            self.button_convert.setEnabled(True)
        else:
            self._reset_ui()
        QMessageBox.critical(self, "エラー", error_msg)

    def closeEvent(self, event):
        """ウィンドウを閉じる前に設定を保存"""
        geometry = WindowGeometry.from_qwidget(self)
        self.config_manager.set_window_geometry(geometry)
        self.config_manager.save()
        event.accept()
