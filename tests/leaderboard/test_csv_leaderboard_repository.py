from __future__ import annotations

import pytest
from pathlib import Path

from OrecchietTetris.leaderboard.csv_leaderboard_repository import CsvLeaderboardRepository
from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry


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


def test_each_construction_returns_distinct_instance(tmp_path: Path) -> None:
    path = tmp_path / "lb.csv"
    a = CsvLeaderboardRepository(path=path)
    b = CsvLeaderboardRepository(path=path)
    assert a is not b


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


def test_name_with_comma_roundtrips(repo: CsvLeaderboardRepository) -> None:
    entry = LeaderboardEntry(name="Rossi, Mario", score=100, level=1, lines=3)
    repo.save(entry)
    assert repo.load_all()[0].name == "Rossi, Mario"


def test_unicode_name_roundtrips(repo: CsvLeaderboardRepository) -> None:
    entry = LeaderboardEntry(name="Ünïcödé", score=200, level=2, lines=6)
    repo.save(entry)
    assert repo.load_all()[0].name == "Ünïcödé"


def test_header_written_only_once(repo: CsvLeaderboardRepository) -> None:
    repo.save(LeaderboardEntry(name="A", score=1, level=1, lines=1))
    repo.save(LeaderboardEntry(name="B", score=2, level=1, lines=1))
    content = repo._path.read_text(encoding="utf-8")
    assert content.count("name,score") == 1


def test_score_tie_returns_both_entries(repo: CsvLeaderboardRepository) -> None:
    repo.save(LeaderboardEntry(name="Alice", score=100, level=1, lines=5))
    repo.save(LeaderboardEntry(name="Bob", score=100, level=2, lines=10))
    entries = repo.load_all()
    assert len(entries) == 2
    assert all(e.score == 100 for e in entries)


def test_zero_score_entry_roundtrips(repo: CsvLeaderboardRepository) -> None:
    entry = LeaderboardEntry(name="Beginner", score=0, level=1, lines=0)
    repo.save(entry)
    assert repo.load_all()[0].score == 0


def test_load_all_returns_list(repo: CsvLeaderboardRepository) -> None:
    assert isinstance(repo.load_all(), list)


def test_higher_score_always_before_lower(repo: CsvLeaderboardRepository) -> None:
    repo.save(LeaderboardEntry(name="Low", score=10, level=1, lines=1))
    repo.save(LeaderboardEntry(name="High", score=9999, level=10, lines=100))
    repo.save(LeaderboardEntry(name="Mid", score=500, level=5, lines=50))
    entries = repo.load_all()
    for i in range(len(entries) - 1):
        assert entries[i].score >= entries[i + 1].score
