from __future__ import annotations

from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry


def test_entry_equality() -> None:
    a = LeaderboardEntry(name="Alice", score=500, level=3, lines=10)
    b = LeaderboardEntry(name="Alice", score=500, level=3, lines=10)
    assert a == b


def test_entry_inequality_by_score() -> None:
    a = LeaderboardEntry(name="Alice", score=500, level=3, lines=10)
    b = LeaderboardEntry(name="Alice", score=600, level=3, lines=10)
    assert a != b


def test_entry_inequality_by_name() -> None:
    a = LeaderboardEntry(name="Alice", score=500, level=3, lines=10)
    b = LeaderboardEntry(name="Bob", score=500, level=3, lines=10)
    assert a != b


def test_entry_fields_are_correct_types() -> None:
    entry = LeaderboardEntry(name="Bob", score=1234, level=5, lines=20)
    assert isinstance(entry.name, str)
    assert isinstance(entry.score, int)
    assert isinstance(entry.level, int)
    assert isinstance(entry.lines, int)


def test_entry_fields_store_given_values() -> None:
    entry = LeaderboardEntry(name="Test", score=42, level=7, lines=99)
    assert entry.name == "Test"
    assert entry.score == 42
    assert entry.level == 7
    assert entry.lines == 99
