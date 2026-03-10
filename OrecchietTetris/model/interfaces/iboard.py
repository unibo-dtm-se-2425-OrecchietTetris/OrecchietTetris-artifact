from __future__ import annotations

from abc import ABC, abstractmethod

from OrecchietTetris.model.interfaces import ITetromino


class IBoard(ABC):
    """Interface for the fixed grid of placed cells."""

    @property
    @abstractmethod
    def rows(self) -> int:
        """Number of rows in the grid."""

    @property
    @abstractmethod
    def cols(self) -> int:
        """Number of columns in the grid."""

    @property
    @abstractmethod
    def grid(self) -> list[list[int]]:
        """Snapshot of the fixed grid (does not include the falling piece)."""

    @abstractmethod
    def is_valid_position(self, tetromino: ITetromino, row: int, col: int) -> bool:
        """Return True if *tetromino* fits at *(row, col)* without overlap or out-of-bounds."""

    @abstractmethod
    def place_tetromino(self, tetromino: ITetromino, row: int, col: int) -> None:
        """Lock *tetromino* into the grid at *(row, col)*."""

    @abstractmethod
    def clear_lines(self) -> int:
        """Remove all complete rows and return the number of rows cleared."""

    @abstractmethod
    def is_game_over(self, tetromino: ITetromino, spawn_col: int) -> bool:
        """Return True if *tetromino* cannot be placed at the spawn row."""

    @abstractmethod
    def reset(self) -> None:
        """Clear the entire grid back to empty."""
