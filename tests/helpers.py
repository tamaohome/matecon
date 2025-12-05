from pathlib import Path


def read_txt_file(filepath: str | Path, encoding: str = "cp932") -> list[str]:
    """テキストファイルを読み込み文字列リストを取得する"""
    filepath = Path(filepath)
    with filepath.open(encoding=encoding) as f:
        return [line.rstrip("\n") for line in f.readlines()]
