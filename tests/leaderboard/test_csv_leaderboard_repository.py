from __future__ import annotations

import pytest
from pathlib import Path

from OrecchietTetris.leaderboard.csv_leaderboard_repository import CsvLeaderboardRepository
from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset the singleton between tests so each test gets a fresh instance."""
    CsvLeaderboardRepository._instance = None
    yield
    CsvLeaderboardRepository._instance = None


@pytest.fixture
def repo(tmp_path: Path) -> CsvLeaderboardRepository:
    return CsvLeaderboardRepository(path=tmp_path / "leaderboard.csv")


def test_load_all_empty(repo: CsvLeaderboardRepository) -> None:
    assert repo.load_all() == []


def test_save_and_load(repo: CsvLeaderboardRepository) -> None:
    entry = LeaderboardEntry(name="Alice", score=500, level=3, lines=10)
    repo.save(entry)
    entries = repo.load_all()
    assert len(entries) == 1
    assert entries[0] == entry


def test_load_all_sorted_by_score_descending(repo: CsvLeaderboardRepository) -> None:
    repo.save(LeaderboardEntry(name="Alice", score=100, level=1, lines=5))
    repo.save(LeaderboardEntry(name="Bob", score=900, level=5, lines=30))
    repo.save(LeaderboardEntry(name="Carol", score=400, level=2, lines=15))

    entries = repo.load_all()
    scores = [e.score for e in entries]
    assert scores == sorted(scores, reverse=True)


def test_multiple_saves_accumulate(repo: CsvLeaderboardRepository) -> None:
    for i in range(3):
        repo.save(LeaderboardEntry(name=f"Player{i}", score=i * 100, level=1, lines=i))
    assert len(repo.load_all()) == 3


def test_singleton_returns_same_instance(tmp_path: Path) -> None:
    path = tmp_path / "lb.csv"
    a = CsvLeaderboardRepository(path=path)
    b = CsvLeaderboardRepository(path=path)
    assert a is b


def test_csv_file_created_on_first_save(tmp_path: Path) -> None:
    path = tmp_path / "sub" / "leaderboard.csv"
    repo = CsvLeaderboardRepository(path=path)
    assert not path.exists()
    repo.save(LeaderboardEntry(name="X", score=0, level=1, lines=0))
    assert path.exists()


def test_entry_fields_roundtrip(repo: CsvLeaderboardRepository) -> None:
    original = LeaderboardEntry(name="Mario Rossi", score=12345, level=7, lines=42)
    repo.save(original)
    loaded = repo.load_all()[0]
    assert loaded.name == original.name
    assert loaded.score == original.score
    assert loaded.level == original.level
    assert loaded.lines == original.lines
