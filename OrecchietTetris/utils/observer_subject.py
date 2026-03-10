from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Any


class EventType(Enum):
    BOARD_UPDATED = "board_updated"   # piece moved or locked; data: None
    NEW_PIECE = "new_piece"           # new piece spawned; data: ITetromino
    LINES_CLEARED = "lines_cleared"   # data: int (number of lines)
    SCORE_UPDATED = "score_updated"   # data: int (new score)
    GAME_OVER = "game_over"           # data: None
    PAUSED = "paused"                 # data: None
    RESUMED = "resumed"               # data: None
    HOLD_UPDATED = "hold_updated"     # data: ITetromino | None (new held piece)


class Subject:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: EventType, data: Any = None) -> None:
        for observer in self._observers:
            observer.update(event, data)


class Observer(ABC):
    @abstractmethod
    def update(self, event_type: EventType, data: Any) -> None:
        """ Handle the event received """
