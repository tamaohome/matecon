from datetime import datetime
from pathlib import Path

from matecon.gui.preferences import with_timestamp_suffix


def test_appends_timestamp_before_extension():
    path = Path("/data/material.txt")

    result = with_timestamp_suffix(path, now=datetime(2026, 11, 12, 15, 30, 5))

    assert result == Path("/data/material_20261112_153005.txt")


def test_keeps_dots_in_stem():
    path = Path("/data/v1.2.material.txt")

    result = with_timestamp_suffix(path, now=datetime(2026, 1, 2, 3, 4, 5))

    assert result == Path("/data/v1.2.material_20260102_030405.txt")
