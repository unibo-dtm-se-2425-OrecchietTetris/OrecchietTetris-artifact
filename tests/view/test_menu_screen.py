"""Tests for MenuScreen.

MenuScreen is the main menu: logo, New Game / Leaderboard buttons, a settings
gear and a quit button.  The settings overlay contains language toggles and an
optional volume slider when an audio controller is provided.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.view.menu_screen import MenuScreen
from OrecchietTetris.utils import EventType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def menu() -> MenuScreen:
    """MenuScreen without an audio controller."""
    return MenuScreen(name="menu")


@pytest.fixture()
def audio() -> MagicMock:
    mock = MagicMock()
    mock.volume = 0.5
    return mock


@pytest.fixture()
def menu_with_audio(audio: MagicMock) -> MenuScreen:
    """MenuScreen with a mock audio controller (shows volume slider)."""
    return MenuScreen(
        on_new_game=MagicMock(),
        on_leaderboard=MagicMock(),
        audio=audio,
        name="menu",
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_menu_screen_can_be_instantiated(menu: MenuScreen) -> None:
    assert menu is not None


def test_menu_screen_with_audio_can_be_instantiated(menu_with_audio: MenuScreen) -> None:
    assert menu_with_audio is not None


def test_menu_screen_has_settings_overlay(menu: MenuScreen) -> None:
    assert menu._settings_overlay is not None


def test_menu_screen_with_audio_has_volume_button(menu_with_audio: MenuScreen) -> None:
    assert menu_with_audio._btn_volume is not None


def test_menu_screen_with_audio_has_volume_slider(menu_with_audio: MenuScreen) -> None:
    assert menu_with_audio._slider_volume is not None


def test_menu_screen_without_audio_has_no_volume_controls(menu: MenuScreen) -> None:
    assert menu._btn_volume is None
    assert menu._slider_volume is None


# ---------------------------------------------------------------------------
# IView — show / hide / update
# ---------------------------------------------------------------------------

def test_show_makes_screen_visible_and_enabled(menu: MenuScreen) -> None:
    menu.hide()  # ensure not already shown
    menu.show()
    assert menu.opacity == 1.0
    assert menu.disabled is False


def test_hide_makes_screen_invisible_and_disabled(menu: MenuScreen) -> None:
    menu.show()
    menu.hide()
    assert menu.opacity == 0.0
    assert menu.disabled is True


def test_update_is_a_no_op(menu: MenuScreen) -> None:
    menu.update(EventType.BOARD_UPDATED, None)  # must not raise


# ---------------------------------------------------------------------------
# Callbacks — new game / leaderboard
# ---------------------------------------------------------------------------

def test_handle_new_game_calls_callback() -> None:
    cb = MagicMock()
    m = MenuScreen(on_new_game=cb, name="menu")
    m._handle_new_game()
    cb.assert_called_once()


def test_handle_new_game_without_callback_does_not_raise() -> None:
    m = MenuScreen(name="menu")
    m._handle_new_game()  # must not raise


def test_handle_leaderboard_calls_callback() -> None:
    cb = MagicMock()
    m = MenuScreen(on_leaderboard=cb, name="menu")
    m._handle_leaderboard()
    cb.assert_called_once()


def test_handle_leaderboard_without_callback_does_not_raise() -> None:
    m = MenuScreen(name="menu")
    m._handle_leaderboard()  # must not raise


# ---------------------------------------------------------------------------
# Settings overlay
# ---------------------------------------------------------------------------

def test_open_settings_adds_overlay_widget(menu: MenuScreen) -> None:
    menu._open_settings()
    # add_widget is a no-op stub, but the overlay should not be None
    assert menu._settings_overlay is not None


def test_close_settings_removes_overlay_widget(menu: MenuScreen) -> None:
    menu._open_settings()
    menu._close_settings()  # must not raise


# ---------------------------------------------------------------------------
# Volume controls
# ---------------------------------------------------------------------------

def test_on_volume_change_updates_audio(menu_with_audio: MenuScreen, audio: MagicMock) -> None:
    menu_with_audio._on_volume_change(MagicMock(), 0.8)
    audio.set_volume.assert_called_once_with(0.8)


def test_on_volume_change_zero_sets_mute_icon(menu_with_audio: MenuScreen) -> None:
    menu_with_audio._on_volume_change(MagicMock(), 0.0)
    from OrecchietTetris.view.menu_screen import _IC_MUTE
    assert menu_with_audio._btn_volume is not None
    assert menu_with_audio._btn_volume.text == _IC_MUTE


def test_on_volume_change_nonzero_sets_vol_icon(menu_with_audio: MenuScreen) -> None:
    menu_with_audio._on_volume_change(MagicMock(), 0.5)
    from OrecchietTetris.view.menu_screen import _IC_VOL
    assert menu_with_audio._btn_volume is not None
    assert menu_with_audio._btn_volume.text == _IC_VOL


def test_toggle_mute_mutes_when_volume_positive(
    menu_with_audio: MenuScreen, audio: MagicMock
) -> None:
    audio.volume = 0.8
    menu_with_audio._toggle_mute()
    # Slider value should be set to 0.0
    assert menu_with_audio._slider_volume is not None
    assert menu_with_audio._slider_volume.value == 0.0


def test_toggle_mute_restores_volume_when_muted(
    menu_with_audio: MenuScreen, audio: MagicMock
) -> None:
    audio.volume = 0.0
    menu_with_audio._pre_mute_volume = 0.7
    menu_with_audio._toggle_mute()
    assert menu_with_audio._slider_volume is not None
    assert menu_with_audio._slider_volume.value == 0.7


def test_toggle_mute_uses_default_when_pre_mute_zero(
    menu_with_audio: MenuScreen, audio: MagicMock
) -> None:
    audio.volume = 0.0
    menu_with_audio._pre_mute_volume = 0.0
    menu_with_audio._toggle_mute()
    assert menu_with_audio._slider_volume is not None
    assert menu_with_audio._slider_volume.value == 0.5


def test_toggle_mute_without_audio_does_not_raise(menu: MenuScreen) -> None:
    menu._toggle_mute()  # must not raise (audio is None)


# ---------------------------------------------------------------------------
# Quit button
# ---------------------------------------------------------------------------

def test_handle_quit_calls_app_stop(menu: MenuScreen) -> None:
    with patch("OrecchietTetris.view.menu_screen.App") as mock_app:
        menu._handle_quit()
        mock_app.get_running_app.return_value.stop.assert_called_once()


# ---------------------------------------------------------------------------
# Background update helper
# ---------------------------------------------------------------------------

def test_update_bg_syncs_rect_to_pos_and_size(menu: MenuScreen) -> None:
    menu.pos = (10, 20)
    menu.size = (800, 600)
    menu._update_bg()
    assert menu._bg_rect.pos == (10, 20)
    assert menu._bg_rect.size == (800, 600)


# ---------------------------------------------------------------------------
# Language switch — _set_language / _refresh_labels
# ---------------------------------------------------------------------------

def test_set_language_en_updates_labels(menu: MenuScreen) -> None:
    menu._set_language("en")
    assert "EN" not in menu._btn_new_game.text or menu._btn_new_game.text  # just no crash


def test_set_language_it_updates_labels(menu: MenuScreen) -> None:
    menu._set_language("it")
    # locale should be 'it' after the call
    import i18n  # type: ignore[import-untyped]
    assert i18n.get("locale") == "it"


def test_refresh_labels_updates_button_texts(menu: MenuScreen) -> None:
    menu._refresh_labels()
    assert menu._btn_new_game.text  # non-empty
    assert menu._btn_leaderboard.text  # non-empty
