import sys
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
        if len(paths):
            return paths
        else:
            raise ValueError()
    except Exception:
        while True:
            p = input("ファイルパスを入力(またはこの画面にファイルをドラッグ): ")
            if p:
                return [Path(p.replace('"', ""))]


def write_txt(org_path: Path | str, lines: list[str]) -> Path:
    """
    指定されたファイルパスに文字列リストを書き出す

    - ファイルパスは `.txt` に変換される
    - エンコードは shift-jis (cp932) 固定
    """

    txt_path = Path(org_path).resolve().with_suffix(".txt")
    with txt_path.open(mode="w", encoding="cp932") as f:
        for line in lines:
            f.write(line + "\n")
    return txt_path
