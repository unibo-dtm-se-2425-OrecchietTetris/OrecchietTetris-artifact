from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

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
    def current_piece(self) -> Optional[ITetromino]:
        """The falling piece currently in play, or None before the game starts."""

    @property
    @abstractmethod
    def current_row(self) -> int:
        """Top row of the falling piece."""

    @property
    @abstractmethod
    def current_col(self) -> int:
        """Left column of the falling piece."""

    @property
    @abstractmethod
    def grid(self) -> list[list[int]]:
        """Snapshot of the fixed grid, including the falling piece."""

    @abstractmethod
    def set_falling_piece(self, piece: ITetromino, row: int, col: int) -> None:
        """Set the current falling piece and its position."""

    @abstractmethod
    def move_falling_piece(self, row: int, col: int) -> bool:
        """Update the position of the current falling piece without changing the piece."""

    @abstractmethod
    def clear_falling_piece(self) -> None:
        """Remove the falling piece reference (called after locking it into the fixed grid)."""

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
        """Clear the entire grid and the falling piece back to empty."""
