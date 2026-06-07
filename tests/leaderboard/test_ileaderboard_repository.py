from __future__ import annotations

import pytest

from OrecchietTetris.leaderboard.interfaces.ileaderboard_repository import ILeaderboardRepository
from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry


def test_interface_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        ILeaderboardRepository()  # type: ignore[abstract]


def test_concrete_implementation_must_provide_save_and_load_all() -> None:
    class MinimalRepo(ILeaderboardRepository):
        def save(self, entry: LeaderboardEntry) -> None:
            pass

        def load_all(self) -> list[LeaderboardEntry]:
            return []

    repo = MinimalRepo()
    repo.save(LeaderboardEntry(name="X", score=0, level=1, lines=0))
    assert repo.load_all() == []


def test_partial_implementation_raises() -> None:
    class MissingSave(ILeaderboardRepository):
        def load_all(self) -> list[LeaderboardEntry]:
            return []
        # save() not implemented

    with pytest.raises(TypeError):
        MissingSave()  # type: ignore[abstract]


def test_partial_implementation_missing_load_all_raises() -> None:
    class MissingLoadAll(ILeaderboardRepository):
        def save(self, entry: LeaderboardEntry) -> None:
            pass
        # load_all() not implemented

    with pytest.raises(TypeError):
        MissingLoadAll()  # type: ignore[abstract]
