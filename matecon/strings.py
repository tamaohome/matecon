# -*- coding: utf-8 -*-

from unicodedata import east_asian_width
from unicodedata import normalize
from typing import Any


def adjust_str(item, width: int | slice, align: Any = "L") -> str:
    """文字列を左右に位置揃え"""
    # item を正規化して _item を定義
    try:
        if item is None:
            _item = ""
        else:
            _item = str(item)
    except TypeError:
        raise TypeError("引数 item の型が不正です:", item)

    # width を正規化して _width を定義
    if isinstance(width, slice):
        _width = width.stop - width.start
    else:
        _width = width
    if _width < 0:
        raise ValueError("引数 width の値が不正です:", width)

    # align を正規化して _align を定義
    if isinstance(align, str):
        if align.upper() in ("", "L", "LEFT"):
            _align = "L"
        elif align.upper() in ("R", "RIGHT"):
            _align = "R"
        else:
            raise ValueError("引数 align の値が不正です:", align)
    else:
        if str(align) == "Align.L":
            _align = "L"
        elif str(align) == "Align.R":
            _align = "R"
        else:
            raise ValueError("引数 align の値が不正です:", align)

    # _item の文字列長さが _width 以上の場合、整形せずそのまま返す
    if _width <= mbstring_len(_item):
        return _item

    # 余白を追加して返す
    fill_space = " " * (_width - mbstring_len(_item))
    if _align == "L":
        return _item + fill_space
    else:
        return fill_space + _item


def mbstring_len(text: str) -> int:
    """文字列幅を返す (半角文字は1文字, 全角文字は2文字換算)"""
    char_count = 0
    for char in text:
        s = east_asian_width(char)
        if s in ("H", "Na", "N"):
            char_count += 1
        elif s in ("F", "W", "A"):
            char_count += 2
        else:
            char_count += 1
    return char_count


def zen2han(value: Any) -> str:
    """全角英数字を半角に変換して返す"""
    value = value if isinstance(value, str) else str(value)
    return normalize("NFKC", value)


def is_valid_chars(*values: Any) -> bool:
    """文字列の有効性をチェック"""

    def is_valid_char(c: int) -> bool:
        # 半角英数
        if 0x0020 <= c <= 0x007E:
            return True
        # 記号
        if chr(c) in ["¥", "¦", "¶", "§", "×", "÷", "±", "←", "↑", "→", "↓"]:
            return True
        if ord("①") <= c <= ord("⑳"):
            return True
        if ord("Ⅰ") <= c <= ord("Ⅻ") or ord("ⅰ") <= c <= ord("ⅻ"):
            return True
        # ギリシャ文字
        if 0x0391 <= c <= 0x03C9:
            return True
        # ひらがな・カタカナ・漢字
        if 0x3000 <= c:
            return True

        return False

    return all(is_valid_char(ord(c)) for value in values for c in str(value))
