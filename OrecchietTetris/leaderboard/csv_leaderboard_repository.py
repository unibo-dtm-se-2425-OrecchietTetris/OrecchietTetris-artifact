from __future__ import annotations

import csv
from pathlib import Path
from typing import ClassVar, Optional

from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry
from OrecchietTetris.leaderboard.interfaces.ileaderboard_repository import ILeaderboardRepository
from OrecchietTetris.utils.paths import ASSETS_DIR

_CSV_FIELDS = ("name", "score", "level", "lines")


class CsvLeaderboardRepository(ILeaderboardRepository):
    """Singleton repository that persists leaderboard entries to a CSV file."""

    _instance: ClassVar[Optional[CsvLeaderboardRepository]] = None

    def __new__(cls, path: Optional[Path] = None) -> CsvLeaderboardRepository:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: Optional[Path] = None) -> None:
        if hasattr(self, "_initialized"):
            return
        self._path: Path = path if path is not None else ASSETS_DIR / "lb" / "leaderboard.csv"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized: bool = True

    def save(self, entry: LeaderboardEntry) -> None:
        write_header = not self._path.exists() or self._path.stat().st_size == 0
        with self._path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow({
                "name": entry.name,
                "score": entry.score,
                "level": entry.level,
                "lines": entry.lines,
            })

    def load_all(self) -> list[LeaderboardEntry]:
        if not self._path.exists() or self._path.stat().st_size == 0:
            return []
        with self._path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            entries = [
                LeaderboardEntry(
                    name=row["name"],
                    score=int(row["score"]),
                    level=int(row["level"]),
                    lines=int(row["lines"]),
                )
                for row in reader
            ]
        return sorted(entries, key=lambda e: e.score, reverse=True)
