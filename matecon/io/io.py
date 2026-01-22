import sys
from collections.abc import Sequence
from pathlib import Path


def get_path_list(ext: str) -> list[Path]:
    """
    指定された拡張子のファイルパスを取得する

    - コマンドライン引数から指定された拡張子のファイルパスを取得する
    - コマンドライン引数に該当するファイルがない場合は、ファイルパスの標準入力を求める
    """

    def _get_paths_from_argv():
        paths = [Path(p.replace('"', "")) for p in sys.argv[1:]]
        return _validated_paths(paths)

    def _validated_paths(paths: list[Path]):
        # オブション引数を除外
        paths = [path for path in paths if not str(path).startswith("-")]
        # 指定された拡張子のファイルを取得
        paths = [path for path in paths if path.suffix.lower() == ext.lower()]
        # 存在するファイルのみを取得
        paths = [path for path in paths if path.exists()]
        return paths

    try:
        paths = _get_paths_from_argv()
        if not paths:
            raise ValueError()
        return paths
    except Exception:
        while True:
            p = input("ファイルパスを入力(またはこの画面にファイルをドラッグ): ")
            if p:
                return [Path(p.replace('"', ""))]


def get_filepaths_from_args(allow_exts: list[str], args: Sequence[str]) -> list[Path]:
    """
    コマンドライン引数からファイルパスのリストを取得する

    無効なパス（ファイルが存在しない、対応形式でない）はスキップされ、警告メッセージが出力される
    """
    filepaths = []

    for arg in args:
        if not arg:
            continue

        # クォート・空白削除
        clean_path = arg.strip('"').strip("'").strip()
        if not clean_path:
            continue

        path = Path(clean_path)

        # ファイル存在確認
        if not path.exists():
            print(f"警告: ファイルが存在しません: {path}")
            continue

        # ファイルであるか確認
        if not path.is_file():
            print(f"警告: ファイルではありません: {path}")
            continue

        # ファイル形式確認
        if path.suffix.lower() not in allow_exts:
            print(f"警告: サポートされていないファイル形式です: {path}")
            continue

        filepaths.append(path)

    return filepaths


def write_text_file(filepath: Path | str, lines: list[str]) -> Path:
    """
    指定されたファイルパスに文字列リストを書き出す

    - ファイルパスは `.txt` に変換される
    - エンコードは shift-jis (cp932) 固定
    """
    text_filepath = Path(filepath).resolve().with_suffix(".txt")
    with text_filepath.open(mode="w", encoding="cp932") as f:
        for line in lines:
            f.write(line + "\n")
    return text_filepath
