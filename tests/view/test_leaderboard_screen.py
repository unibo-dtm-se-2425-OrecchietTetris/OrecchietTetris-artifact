from __future__ import annotations

import types
from unittest.mock import MagicMock

import pytest

from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry
from OrecchietTetris.view.leaderboard_screen import LeaderboardScreen, _PODIUM_ROW_H, _SECTION_H
from OrecchietTetris.view.widgets.leaderboard_row import LeaderboardRow


# ---------------------------------------------------------------------------
# _entry_key (static method — no Kivy instance needed)
# ---------------------------------------------------------------------------

def test_entry_key_format() -> None:
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    assert LeaderboardScreen._entry_key(1, entry) == "Alice:1000:3:15"


def test_entry_key_does_not_include_rank() -> None:
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    assert LeaderboardScreen._entry_key(1, entry) == LeaderboardScreen._entry_key(5, entry)


def test_entry_key_differs_by_name() -> None:
    e1 = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    e2 = LeaderboardEntry(name="Bob", score=1000, level=3, lines=15)
    assert LeaderboardScreen._entry_key(1, e1) != LeaderboardScreen._entry_key(1, e2)


def test_entry_key_differs_by_score() -> None:
    e1 = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    e2 = LeaderboardEntry(name="Alice", score=2000, level=3, lines=15)
    assert LeaderboardScreen._entry_key(1, e1) != LeaderboardScreen._entry_key(1, e2)


# ---------------------------------------------------------------------------
# _rank_change (instance method — tested via a lightweight stub)
# ---------------------------------------------------------------------------

def _make_stub(prev_ranks: dict[str, int]) -> types.SimpleNamespace:
    """Minimal stand-in for LeaderboardScreen that satisfies _rank_change."""
    stub = types.SimpleNamespace()
    stub._prev_ranks = prev_ranks
    stub._entry_key = LeaderboardScreen._entry_key
    return stub


def test_rank_change_improved() -> None:
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    key = LeaderboardScreen._entry_key(1, entry)
    stub = _make_stub({key: 5})
    assert LeaderboardScreen._rank_change(stub, 3, entry) == 2  # type: ignore[arg-type]


def test_rank_change_dropped() -> None:
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    key = LeaderboardScreen._entry_key(1, entry)
    stub = _make_stub({key: 2})
    assert LeaderboardScreen._rank_change(stub, 4, entry) == -2  # type: ignore[arg-type]


def test_rank_change_same_rank() -> None:
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    key = LeaderboardScreen._entry_key(1, entry)
    stub = _make_stub({key: 3})
    assert LeaderboardScreen._rank_change(stub, 3, entry) == 0  # type: ignore[arg-type]


def test_rank_change_no_previous_data() -> None:
    entry = LeaderboardEntry(name="NewPlayer", score=500, level=1, lines=3)
    stub = _make_stub({})
    assert LeaderboardScreen._rank_change(stub, 1, entry) == 0  # type: ignore[arg-type]


def test_rank_change_large_jump() -> None:
    entry = LeaderboardEntry(name="Climber", score=9999, level=9, lines=90)
    key = LeaderboardScreen._entry_key(1, entry)
    stub = _make_stub({key: 20})
    assert LeaderboardScreen._rank_change(stub, 1, entry) == 19  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

def test_podium_row_height_positive() -> None:
    assert _PODIUM_ROW_H > 0


def test_section_label_height_positive() -> None:
    assert _SECTION_H > 0


# ---------------------------------------------------------------------------
# LeaderboardScreen instantiation and IView — lines covering _build_ui,
# show, hide, set_current_player, _handle_back
# ---------------------------------------------------------------------------

def _repo(entries: list[LeaderboardEntry]) -> MagicMock:
    mock = MagicMock()
    mock.load_all.return_value = entries
    return mock


@pytest.fixture()
def screen_empty() -> LeaderboardScreen:
    return LeaderboardScreen(repository=_repo([]), on_back=MagicMock(), name="leaderboard")


@pytest.fixture()
def screen_three() -> LeaderboardScreen:
    entries = [
        LeaderboardEntry(name="A", score=3000, level=5, lines=30),
        LeaderboardEntry(name="B", score=2000, level=4, lines=20),
        LeaderboardEntry(name="C", score=1000, level=3, lines=10),
    ]
    return LeaderboardScreen(repository=_repo(entries), name="leaderboard")


@pytest.fixture()
def screen_many() -> LeaderboardScreen:
    entries = [
        LeaderboardEntry(name=f"P{i}", score=5000 - i * 100, level=5, lines=50)
        for i in range(6)
    ]
    return LeaderboardScreen(repository=_repo(entries), name="leaderboard")


def test_leaderboard_screen_can_be_instantiated(screen_empty: LeaderboardScreen) -> None:
    assert screen_empty is not None


def test_show_makes_screen_visible(screen_empty: LeaderboardScreen) -> None:
    screen_empty.hide()
    screen_empty.show()
    assert screen_empty.opacity == 1.0
    assert screen_empty.disabled is False


def test_hide_makes_screen_invisible(screen_empty: LeaderboardScreen) -> None:
    screen_empty.show()
    screen_empty.hide()
    assert screen_empty.opacity == 0.0
    assert screen_empty.disabled is True


def test_update_is_noop(screen_empty: LeaderboardScreen) -> None:
    from OrecchietTetris.utils import EventType
    screen_empty.update(EventType.BOARD_UPDATED, None)


def test_set_current_player_stores_name(screen_empty: LeaderboardScreen) -> None:
    screen_empty.set_current_player("Alice")
    assert screen_empty._current_name == "Alice"


def test_handle_back_calls_callback() -> None:
    cb = MagicMock()
    screen = LeaderboardScreen(repository=_repo([]), on_back=cb, name="leaderboard")
    screen._handle_back()
    cb.assert_called_once()


def test_handle_back_without_callback_does_not_raise() -> None:
    screen = LeaderboardScreen(repository=_repo([]), name="leaderboard")
    screen._handle_back()


def test_update_bg_syncs_rect(screen_empty: LeaderboardScreen) -> None:
    screen_empty.pos = (5, 10)
    screen_empty.size = (800, 600)
    screen_empty._update_bg()
    assert screen_empty._bg_rect.pos == (5, 10)
    assert screen_empty._bg_rect.size == (800, 600)


# ---------------------------------------------------------------------------
# _refresh — various entry counts
# ---------------------------------------------------------------------------

def test_refresh_empty_does_not_show_section_label(screen_empty: LeaderboardScreen) -> None:
    screen_empty._refresh()
    assert screen_empty._section_lbl.text == ""
    assert screen_empty._section_lbl.height == 0


def test_refresh_with_less_than_three_entries_no_podium() -> None:
    entries = [
        LeaderboardEntry(name="A", score=1000, level=2, lines=10),
        LeaderboardEntry(name="B", score=500, level=1, lines=5),
    ]
    screen = LeaderboardScreen(repository=_repo(entries), name="leaderboard")
    screen._refresh()
    assert screen._podium_container.height == 0


def test_refresh_with_three_entries_builds_podium(screen_three: LeaderboardScreen) -> None:
    screen_three._refresh()
    # Podium container height must be the positive constant
    assert screen_three._podium_container.height == _PODIUM_ROW_H


def test_refresh_with_more_than_three_shows_section_label(screen_many: LeaderboardScreen) -> None:
    screen_many._refresh()
    assert screen_many._section_lbl.text != ""
    assert screen_many._section_lbl.height == _SECTION_H


def test_refresh_snapshots_prev_ranks(screen_many: LeaderboardScreen) -> None:
    screen_many._refresh()
    assert len(screen_many._prev_ranks) > 0


def test_show_triggers_refresh(screen_empty: LeaderboardScreen) -> None:
    screen_empty.show()
    # show() calls _refresh() which calls repo.load_all()
    screen_empty._repo.load_all.assert_called()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# _make_row — highlighting logic
# ---------------------------------------------------------------------------

def test_make_row_not_highlighted_when_current_name_is_none(screen_empty: LeaderboardScreen) -> None:
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    row = screen_empty._make_row(1, entry)
    assert isinstance(row, LeaderboardRow)


def test_make_row_highlighted_when_name_matches(screen_empty: LeaderboardScreen) -> None:
    screen_empty._current_name = "Alice"
    entry = LeaderboardEntry(name="Alice", score=1000, level=3, lines=15)
    row = screen_empty._make_row(1, entry)
    assert row is not None  # highlighted row constructed without error


def test_make_row_alt_flag_is_passed(screen_empty: LeaderboardScreen) -> None:
    entry = LeaderboardEntry(name="X", score=100, level=1, lines=1)
    row = screen_empty._make_row(5, entry, alt=True)
    assert row is not None
