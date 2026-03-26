from __future__ import annotations

from abc import ABC, abstractmethod

from OrecchietTetris.model.interfaces.itetromino import ITetromino


class ITetrominoFactory(ABC):
    """Interface for tetromino factories.

    Concrete implementations decide *how* the next piece is selected
    (pure random, 7-bag, seeded, etc.).  ``Tetris`` depends only on
    this interface, not on any specific strategy.
    """

    @abstractmethod
    def create_tetromino(self) -> ITetromino:
        """Return a new tetromino (the selection strategy is up to the implementation)."""

    @abstractmethod
    def reset(self) -> None:
        """Reset factory state. Called by ``Tetris.start()`` at the start of every game."""
