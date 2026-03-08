from typing import List

import pytest

from OrecchietTetris.model import Tetromino, ShapeType


def test_tetromino_initialization():
    t = Tetromino()
    assert isinstance(t.shape_type, str)
    assert isinstance(t.shape, list)
    assert len(t.shape) > 0


def test_full_rotation_cycle():
    """ Given any tetromino, 4 rotation should bring the object to the original position """
    t = Tetromino()
    original_shape = t.shape

    for _ in range(4):
        t.rotate()

    assert t.shape == original_shape


@pytest.mark.parametrize("shape_input, expected_output", [
    (ShapeType.I_SHAPE, [[1], [1], [1], [1]]),        # I-shape rotation
    (ShapeType.O_SHAPE, [[1, 1], [1, 1]]),            # O-shape rotation
    (ShapeType.T_SHAPE, [[1, 0], [1, 1], [1, 0]]),    # T-shape rotation
    (ShapeType.S_SHAPE, [[1, 0], [1, 1], [0, 1]]),    # S-shape rotation
    (ShapeType.Z_SHAPE, [[0, 1], [1, 1], [1, 0]]),    # Z-shape rotation
    (ShapeType.J_SHAPE, [[1, 1], [1, 0], [1, 0]]),    # J-shape rotation
    (ShapeType.L_SHAPE, [[1, 0], [1, 0], [1, 1]]),    # L-shape rotation
])
def test_rotations(shape_input: ShapeType, expected_output: List[List[int]]) -> None:
    t = Tetromino(shape_input)
    t.rotate()
    assert repr(t) == f"Tetromino({shape_input.name})"
    assert t.shape == expected_output
