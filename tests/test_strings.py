# -*- coding: utf-8 -*-

from matecon.strings import adjust_str
from matecon.strings import mbstring_len
from matecon.strings import zen2han
from matecon.strings import is_valid_chars
from matecon.templates import Align


def test_adjust_str():
    assert adjust_str("テスト", 8) == "テスト  "
    assert adjust_str("ﾃｽﾄ", 8, "L") == "ﾃｽﾄ     "
    assert adjust_str("123あ漢", 9, "R") == "  123あ漢"

    assert adjust_str("左揃え", 12, Align.L) == "左揃え      "
    assert adjust_str("右揃えﾃｷｽﾄ", 12, Align.R) == "  右揃えﾃｷｽﾄ"

    assert adjust_str(123, 5, Align.R) == "  123"  # int
    assert adjust_str(4.5, 8, Align.R) == "     4.5"  # float
    assert adjust_str(None, 2, Align.L) == "  "  # None


def test_mbstring_len():
    assert mbstring_len("Abc123.,|") == 9
    assert mbstring_len("半角ｶﾅ") == 6
    assert mbstring_len("2バイト文字") == 11
    assert mbstring_len("＊┓〈《【Σφ") == 14

    assert mbstring_len("†") == 2
    assert mbstring_len("§") == 2
    assert mbstring_len("±") == 2
    assert mbstring_len("※") == 2
    assert mbstring_len("↔") == 2


def test_zen2han():
    assert zen2han(123) == "123"
    assert zen2han("－２４０") == "-240"

    assert zen2han("ＡＢＣａｂｃ１２３") == "ABCabc123"
    assert zen2han("テスト") == "テスト"  # 全角カタカナはそのまま
    assert zen2han("！＃＄％＆") == "!#$%&"
    assert zen2han("０１２３４５６７８９") == "0123456789"
    assert zen2han("ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ") == "abcdefghijklmnopqrstuvwxyz"
    assert zen2han("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ") == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def test_is_valid_chars():
    # 半角英数字
    assert is_valid_chars("ABC abc 123")
    # 全角英数字
    assert is_valid_chars("ＡＢＣ　ａｂｃ　１２３")
    # 記号
    assert is_valid_chars("!@#$%^&*()`'\"/\\")
    assert is_valid_chars("！＠＃＄％＾＆＊（）｀＇＂／＼")
    assert is_valid_chars("＋ー×÷")
    assert is_valid_chars("⑮")
    assert is_valid_chars("Ⅶ ⅳ")
    # False が返る文字
    assert not is_valid_chars("⛳")
    # ギリシャ文字
    assert is_valid_chars("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ")
    assert is_valid_chars("αβγδεζηθικλμνξοπρσςτυφχψω")
    assert is_valid_chars("＊〈《【Σφ")
    # 複数
    assert is_valid_chars("ひらがな", "カタカナ", "半角ｶﾅ", "漢字")
    names = ("§3.2", "Σ＝", "＜１＞", "<2>", "【適用基準】")
    assert is_valid_chars(*names)
    # str 以外は常に True
    assert is_valid_chars(320)
    assert is_valid_chars(-98, 0, 5.678, False, True)
