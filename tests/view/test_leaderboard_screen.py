from __future__ import annotations

import types

from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry
from OrecchietTetris.view.leaderboard_screen import LeaderboardScreen, _PODIUM_ROW_H, _SECTION_H


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
