"""Tests for TetrisApp (app.py).

TetrisApp is the Kivy entry point.  Its build() method wires together the
model, audio, leaderboard repo, and all three screens.  Screen-transition
methods delegate to screens (show/hide, begin/end).

We mock all heavy dependencies so the test suite stays fast and headless.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.view.app import TetrisApp


@pytest.fixture()
def app() -> TetrisApp:
    """TetrisApp instance with all heavy collaborators replaced by mocks."""
    with (
        patch("OrecchietTetris.view.app.LabelBase"),
        patch("OrecchietTetris.view.app.Tetris", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.CsvLeaderboardRepository", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.KivyAudioService", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.MenuScreen", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.GameScreen", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.LeaderboardScreen", return_value=MagicMock()),
    ):
        instance = TetrisApp()
        instance.build()
    return instance


# ---------------------------------------------------------------------------
# build() — verifies screen / model / audio wiring
# ---------------------------------------------------------------------------

def test_build_returns_screen_manager(app: TetrisApp) -> None:
    assert app._sm is not None


def test_build_creates_model(app: TetrisApp) -> None:
    assert app._model is not None


def test_build_creates_audio_and_starts_playback(app: TetrisApp) -> None:
    assert app._audio is not None
    app._audio.play.assert_called_once()  # type: ignore[attr-defined]


def test_build_creates_all_three_screens(app: TetrisApp) -> None:
    assert app._menu is not None
    assert app._game is not None
    assert app._leaderboard is not None


def test_build_registers_material_icons_font() -> None:
    with (
        patch("OrecchietTetris.view.app.LabelBase") as mock_lb,
        patch("OrecchietTetris.view.app.Tetris", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.CsvLeaderboardRepository", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.KivyAudioService", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.MenuScreen", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.GameScreen", return_value=MagicMock()),
        patch("OrecchietTetris.view.app.LeaderboardScreen", return_value=MagicMock()),
    ):
        a = TetrisApp()
        a.build()
        mock_lb.register.assert_called_once()
        call_args = mock_lb.register.call_args
        name_kwarg = (
            call_args.kwargs.get("name")
            or call_args[1].get("name")
            or call_args[0][0]
        )
        assert name_kwarg == "MaterialIcons"


# ---------------------------------------------------------------------------
# _start_game — lines 81-86
# ---------------------------------------------------------------------------

def test_start_game_shows_game_and_hides_menu(app: TetrisApp) -> None:
    app._start_game()
    app._game.show.assert_called_once()  # type: ignore[attr-defined]
    app._menu.hide.assert_called_once()  # type: ignore[attr-defined]


def test_start_game_begins_game_loop(app: TetrisApp) -> None:
    app._start_game()
    app._game.begin.assert_called_once()  # type: ignore[attr-defined]


def test_start_game_switches_screen_to_game(app: TetrisApp) -> None:
    app._start_game()
    assert app._sm.current == "game"


# ---------------------------------------------------------------------------
# _back_to_menu — lines 88-93
# ---------------------------------------------------------------------------

def test_back_to_menu_ends_game_loop(app: TetrisApp) -> None:
    app._back_to_menu()
    app._game.end.assert_called_once()  # type: ignore[attr-defined]


def test_back_to_menu_shows_menu_and_hides_game(app: TetrisApp) -> None:
    app._back_to_menu()
    app._game.hide.assert_called_once()  # type: ignore[attr-defined]
    app._menu.show.assert_called_once()  # type: ignore[attr-defined]


def test_back_to_menu_switches_screen_to_menu(app: TetrisApp) -> None:
    app._back_to_menu()
    assert app._sm.current == "menu"


# ---------------------------------------------------------------------------
# _show_leaderboard — lines 95-99
# ---------------------------------------------------------------------------

def test_show_leaderboard_shows_leaderboard_and_hides_menu(app: TetrisApp) -> None:
    app._show_leaderboard()
    app._leaderboard.show.assert_called_once()  # type: ignore[attr-defined]
    app._menu.hide.assert_called_once()  # type: ignore[attr-defined]


def test_show_leaderboard_switches_screen(app: TetrisApp) -> None:
    app._show_leaderboard()
    assert app._sm.current == "leaderboard"


# ---------------------------------------------------------------------------
# _back_to_menu_from_leaderboard — lines 101-105
# ---------------------------------------------------------------------------

def test_back_from_leaderboard_shows_menu(app: TetrisApp) -> None:
    app._back_to_menu_from_leaderboard()
    app._leaderboard.hide.assert_called_once()  # type: ignore[attr-defined]
    app._menu.show.assert_called_once()  # type: ignore[attr-defined]


def test_back_from_leaderboard_switches_screen(app: TetrisApp) -> None:
    app._back_to_menu_from_leaderboard()
    assert app._sm.current == "menu"


# ---------------------------------------------------------------------------
# _on_name_saved — line 107-109
# ---------------------------------------------------------------------------

def test_on_name_saved_forwards_name_to_leaderboard(app: TetrisApp) -> None:
    app._on_name_saved("Alice")
    app._leaderboard.set_current_player.assert_called_once_with("Alice")  # type: ignore[attr-defined]
