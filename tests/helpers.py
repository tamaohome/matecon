# -*- coding: utf-8 -*-

from pathlib import Path


def load_txt_sample(filepath: str | Path, encoding: str = "cp932") -> list[str]:
    """指定されたファイルからテキスト行を読み込む"""
    filepath = Path(filepath)
    with filepath.open(encoding=encoding) as f:
        return [line.rstrip("\n") for line in f.readlines()]
