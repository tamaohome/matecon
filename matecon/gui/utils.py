import sys
from pathlib import Path


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
