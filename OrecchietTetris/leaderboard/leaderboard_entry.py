from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LeaderboardEntry:
    name: str
    score: int
    level: int
    lines: int
