from matecon.gui.preferences import DEFAULT_TIMESTAMP_SUFFIX, PreferencesSettings


def test_timestamp_suffix_default_is_disabled():
    settings = PreferencesSettings()

    assert settings.is_timestamp_suffix_enabled() is DEFAULT_TIMESTAMP_SUFFIX
    assert DEFAULT_TIMESTAMP_SUFFIX is False


def test_timestamp_suffix_round_trip():
    PreferencesSettings().set_timestamp_suffix_enabled(True)

    # 別インスタンスから読み直して永続化を確認する
    assert PreferencesSettings().is_timestamp_suffix_enabled() is True


def test_timestamp_suffix_can_be_turned_off():
    PreferencesSettings().set_timestamp_suffix_enabled(True)

    PreferencesSettings().set_timestamp_suffix_enabled(False)

    assert PreferencesSettings().is_timestamp_suffix_enabled() is False
