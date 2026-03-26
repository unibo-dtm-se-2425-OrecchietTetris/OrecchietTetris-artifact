from __future__ import annotations

import random

from OrecchietTetris.model.interfaces import ITetrominoFactory, ITetromino
from OrecchietTetris.model.tetromino import Tetromino, ShapeType


class BagTetrominoFactory(ITetrominoFactory):
    """7-bag randomizer.

    Maintains a shuffled bag of all 7 ``ShapeType`` values.  When the bag
    empties, it is refilled with all 7 shapes and reshuffled before the next
    piece is drawn.  ``reset()`` clears the bag so the next draw triggers a
    fresh shuffle — call it at the start of every new game.
    """

    def __init__(self) -> None:
        self._bag: list[ShapeType] = []

    def create_tetromino(self) -> ITetromino:
        if not self._bag:
            self._bag = list(ShapeType)
            random.shuffle(self._bag)
        return Tetromino(self._bag.pop())

    def reset(self) -> None:
        self._bag = []
