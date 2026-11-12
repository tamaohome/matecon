import pytest
from PySide6.QtWidgets import QDialogButtonBox

from matecon.gui.preferences import PreferencesDialog, PreferencesSettings


@pytest.fixture
def settings() -> PreferencesSettings:
    return PreferencesSettings()


def _button(dialog: PreferencesDialog, which: QDialogButtonBox.StandardButton):
    return dialog._button_box.button(which)


def test_dialog_reflects_saved_value(qtbot, settings):
    settings.set_timestamp_suffix_enabled(True)

    dialog = PreferencesDialog(settings)
    qtbot.addWidget(dialog)

    assert dialog._chk_timestamp_suffix.isChecked() is True


def test_ok_saves_changed_value_and_emits_signal(qtbot, settings):
    dialog = PreferencesDialog(settings)
    qtbot.addWidget(dialog)

    dialog._chk_timestamp_suffix.setChecked(True)
    with qtbot.waitSignal(dialog.preferencesSaved, timeout=1000):
        _button(dialog, QDialogButtonBox.StandardButton.Ok).click()

    assert settings.is_timestamp_suffix_enabled() is True


def test_cancel_does_not_save(qtbot, settings):
    dialog = PreferencesDialog(settings)
    qtbot.addWidget(dialog)

    dialog._chk_timestamp_suffix.setChecked(True)
    _button(dialog, QDialogButtonBox.StandardButton.Cancel).click()

    assert settings.is_timestamp_suffix_enabled() is False
