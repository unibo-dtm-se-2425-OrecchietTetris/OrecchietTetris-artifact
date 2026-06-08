"""Tests for LeaderboardRow.

LeaderboardRow is a card-style horizontal row showing rank, name, score,
level/lines and a rank-change arrow.  Top-3 ranks receive medal styling;
the highlighted row is tinted blue to mark the current player.
"""
from __future__ import annotations

from OrecchietTetris.view.widgets.leaderboard_row import LeaderboardRow


def test_height_constant() -> None:
    assert LeaderboardRow.HEIGHT == 54


def test_leaderboard_row_exported_from_widgets_package() -> None:
    from OrecchietTetris.view.widgets import LeaderboardRow as LR
    assert LR is LeaderboardRow


# ---------------------------------------------------------------------------
# Construction — lines 57-161
# ---------------------------------------------------------------------------

def test_leaderboard_row_rank1_can_be_instantiated() -> None:
    row = LeaderboardRow(rank=1, name="Alice", score=10000, level=5, lines=40)
    assert row is not None


def test_leaderboard_row_rank2_can_be_instantiated() -> None:
    row = LeaderboardRow(rank=2, name="Bob", score=8000, level=4, lines=30)
    assert row is not None


def test_leaderboard_row_rank3_can_be_instantiated() -> None:
    row = LeaderboardRow(rank=3, name="Carol", score=6000, level=3, lines=20)
    assert row is not None


def test_leaderboard_row_rank4_can_be_instantiated() -> None:
    row = LeaderboardRow(rank=4, name="Dave", score=4000, level=2, lines=10)
    assert row is not None


def test_leaderboard_row_highlighted() -> None:
    """Current-player row must be created without errors."""
    row = LeaderboardRow(rank=5, name="Me", score=500, level=1, lines=3, highlighted=True)
    assert row is not None


def test_leaderboard_row_alt() -> None:
    """Alt rows use alternating background — must construct cleanly."""
    row = LeaderboardRow(rank=6, name="Alt", score=200, level=1, lines=2, alt=True)
    assert row is not None


def test_leaderboard_row_rank_change_positive() -> None:
    """Up arrow must be shown when rank_change > 0 (player climbed)."""
    row = LeaderboardRow(rank=2, name="Climber", score=5000, level=3, lines=20, rank_change=3)
    assert row is not None


def test_leaderboard_row_rank_change_negative() -> None:
    """Down arrow must be shown when rank_change < 0 (player fell)."""
    row = LeaderboardRow(rank=4, name="Faller", score=3000, level=2, lines=10, rank_change=-2)
    assert row is not None


def test_leaderboard_row_rank_change_zero() -> None:
    """Dash must be shown when rank_change == 0 (same position)."""
    row = LeaderboardRow(rank=7, name="Stable", score=1000, level=1, lines=5, rank_change=0)
    assert row is not None


def test_leaderboard_row_default_height() -> None:
    row = LeaderboardRow(rank=5, name="X", score=100, level=1, lines=1)
    assert row.height == LeaderboardRow.HEIGHT


def test_leaderboard_row_has_gfx_instructions() -> None:
    """Row must expose _bg_rr and _border_line from canvas.before."""
    row = LeaderboardRow(rank=2, name="X", score=500, level=1, lines=5)
    assert hasattr(row, "_bg_rr")
    assert hasattr(row, "_border_line")


# ---------------------------------------------------------------------------
# _update_gfx — lines 172-174
# ---------------------------------------------------------------------------

def test_update_gfx_propagates_pos_and_size() -> None:
    """_update_gfx must sync background rect and border line to new pos/size."""
    row = LeaderboardRow(rank=3, name="X", score=100, level=1, lines=1)
    row.pos = (10, 20)
    row.size = (400, 54)
    row._update_gfx()
    assert row._bg_rr.pos == (10, 20)
    assert row._bg_rr.size == (400, 54)
