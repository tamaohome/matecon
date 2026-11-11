from pathlib import Path

from matecon.gui.preferences import DEFAULT_TIMESTAMP_SUFFIX, PreferencesSettings


def _make(path: Path) -> PreferencesSettings:
    return PreferencesSettings(settings_path=str(path))


def test_timestamp_suffix_default_is_disabled(tmp_path: Path):
    settings = _make(tmp_path / "prefs.ini")

    assert settings.is_timestamp_suffix_enabled() is DEFAULT_TIMESTAMP_SUFFIX
    assert DEFAULT_TIMESTAMP_SUFFIX is False


def test_timestamp_suffix_round_trip(tmp_path: Path):
    path = tmp_path / "prefs.ini"

    _make(path).set_timestamp_suffix_enabled(True)

    # 別インスタンスから読み直して永続化を確認する
    assert _make(path).is_timestamp_suffix_enabled() is True


def test_timestamp_suffix_can_be_turned_off(tmp_path: Path):
    path = tmp_path / "prefs.ini"
    _make(path).set_timestamp_suffix_enabled(True)

    _make(path).set_timestamp_suffix_enabled(False)

    assert _make(path).is_timestamp_suffix_enabled() is False
