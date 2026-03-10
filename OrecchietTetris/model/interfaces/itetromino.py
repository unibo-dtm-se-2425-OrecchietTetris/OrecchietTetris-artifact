from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ITetromino(ABC):
    """Interface for a Tetris piece."""

    @property
    @abstractmethod
    def shape_type(self) -> str:
        """Name of the piece shape (e.g. 'I_SHAPE')."""

    @property
    @abstractmethod
    def shape(self) -> list[list[Any]]:
        """Current 2-D matrix representing the piece (1 = filled cell)."""

    @abstractmethod
    def rotate(self) -> None:
        """Rotate the piece 90° clockwise in place."""
