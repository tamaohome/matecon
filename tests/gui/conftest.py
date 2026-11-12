from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_ini_path(tmp_path: Path, monkeypatch) -> Path:
    """GUI テストの設定ファイルを一時ディレクトリに向け、実際の matecon.ini を触らないようにする"""
    ini_path = tmp_path / "prefs.ini"
    monkeypatch.setattr(
        "matecon.gui.preferences.get_ini_path",
        lambda filename=None: str(ini_path),
    )
    return ini_path
