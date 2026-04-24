from __future__ import annotations

from abc import ABC, abstractmethod

from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry


class ILeaderboardRepository(ABC):
    """Persistent storage contract for leaderboard entries."""

    @abstractmethod
    def save(self, entry: LeaderboardEntry) -> None:
        """Persist a new entry."""

    @abstractmethod
    def load_all(self) -> list[LeaderboardEntry]:
        """Return all entries sorted by score descending."""
