# -*- coding: utf-8 -*-

from matecon.position import Position


def test_position():
    pos = Position(3, 2)
    assert str(pos) == "(3, 2)"

    assert pos == Position(3, 2)
    assert pos != Position(5, 2)
    assert pos != Position(3, 9)

    pos2 = Position(-10, -8)
    assert pos2 == Position(0, 0)


def test_position_calc():
    pos1 = Position(12, 100)
    pos2 = Position(20, 30)
    assert pos1 + pos2 == Position(32, 130)
    assert pos1 - pos2 == Position(0, 70)
