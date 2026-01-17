import tempfile
from pathlib import Path

import pytest

from matecon.utils.collections import PathSet


def test_add_and_contains():
    """`add` とリスト操作の基本動作"""
    ps = PathSet(["initial.txt"])
    ps.add("addend.txt")
    assert "initial.txt" in ps
    assert "addend.txt" in ps
    assert Path("initial.txt") in ps
    assert Path("addend.txt") in ps
    assert ps[0].name == "initial.txt"
    assert ps[-1].name == "addend.txt"
    assert len(ps) == 2


def test_path_normalization():
    """`PathSet` に追加したファイルパスは正規化される"""
    ps = PathSet()
    ps.add("./sample.txt")
    assert Path("sample.txt") in ps
    assert "./sample.txt" in ps


def test_discard():
    """`discard` による削除動作"""
    ps = PathSet(["a.txt", "b.txt"])
    ps.discard("a.txt")
    assert "a.txt" not in ps
    ps.discard("not_exist.txt")  # 例外が出ない
    assert len(ps) == 1


def test_order_and_getitem():
    """順序とインデックスアクセス"""
    ps = PathSet(["a.txt", "b.txt", "c.txt"])
    # イテラブルとしての順序をチェック
    assert list(ps)[0] == Path("a.txt").resolve(strict=False)
    # __getitem__ によるインデックスアクセスをチェック
    assert ps[1] == Path("b.txt").resolve(strict=False)


def test_path_equivalence():
    """正規化されたパスの同一性"""
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = Path(tmpdir) / "sample.txt"
        p2 = Path(tmpdir) / "./sample.txt"
        ps = PathSet([p1])
        # PathSet.__contains__() では Path.resolve(strict=False) で正規化されて比較する
        assert p2 in ps


def test_repr():
    """reprの出力"""
    ps = PathSet(["sample.txt"])
    r = repr(ps)
    assert r.startswith("PathSet([")


def test_type_error():
    """`add` に不正な型を渡した場合は `TypeError` が発生する"""
    ps = PathSet()
    with pytest.raises(TypeError):
        ps.add(123)  # type: ignore
