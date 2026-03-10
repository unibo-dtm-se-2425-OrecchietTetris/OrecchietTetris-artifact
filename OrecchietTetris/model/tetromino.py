import random
from enum import Enum
from typing import Any

from OrecchietTetris.model.interfaces import ITetromino


class ShapeType(Enum):
    I_SHAPE = ((1, 1, 1, 1),)
    O_SHAPE = ((2, 2),
               (2, 2))
    T_SHAPE = ((0, 3, 0),
               (3, 3, 3))
    S_SHAPE = ((0, 4, 4),
               (4, 4, 0))
    Z_SHAPE = ((5, 5, 0),
               (0, 6, 6))
    J_SHAPE = ((7, 0, 0),
               (7, 7, 7))
    L_SHAPE = ((0, 0, 8),
               (8, 8, 8))


class Tetromino(ITetromino):
    def __init__(self, shape_type: ShapeType = None):
        if shape_type is None:
            shape_type = random.choice(list(ShapeType))
        self.__shape_type = shape_type.name
        self.__shape = [list(row) for row in shape_type.value]

    @property
    def shape_type(self) -> str:
        return self.__shape_type

    @property
    def shape(self) -> list[list[Any]]:
        return self.__shape

    def rotate(self) -> None:
        self.__shape = [list(row) for row in zip(*self.__shape[::-1])]

    def __repr__(self) -> str:
        return f"Tetromino({self.__shape_type})"
