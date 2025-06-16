# -*- coding: utf-8 -*-

from unicodedata import east_asian_width
from pathlib import Path

import sys


# TODO: 複数パスの入力に対応する
def get_path_list(ext: str) -> list[Path]:
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
    except:
        while True:
            p = input("ファイルパスを入力(またはこの画面にファイルをドラッグ): ")
            if p:
                return [Path(p.replace('"', ""))]


def write_txt(org_path: Path | str, lines: list[str]) -> None:
    txt_path = Path(org_path).resolve().with_suffix(".txt")
    with txt_path.open(mode="w", encoding="cp932") as f:
        for line in lines:
            f.write(line + "\n")

    print("書き込みが完了しました。", txt_path)
