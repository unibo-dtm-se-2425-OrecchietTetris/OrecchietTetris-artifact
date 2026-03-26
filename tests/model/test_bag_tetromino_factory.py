from __future__ import annotations

from OrecchietTetris.model.bag_tetromino_factory import BagTetrominoFactory
from OrecchietTetris.model.tetromino import ShapeType

_ALL_NAMES = {s.name for s in ShapeType}


def test_first_bag_contains_all_shapes() -> None:
    """The first 7 pieces must cover every ShapeType exactly."""
    factory = BagTetrominoFactory()
    pieces = [factory.create_tetromino() for _ in range(7)]
    assert {p.shape_type for p in pieces} == _ALL_NAMES


def test_first_bag_no_duplicates() -> None:
    """No shape appears twice within the same bag of 7."""
    factory = BagTetrominoFactory()
    shape_types = [factory.create_tetromino().shape_type for _ in range(7)]
    assert len(shape_types) == len(set(shape_types))


def test_second_bag_also_complete() -> None:
    """After 14 calls the second batch of 7 also covers all shapes."""
    factory = BagTetrominoFactory()
    pieces = [factory.create_tetromino() for _ in range(14)]
    assert {p.shape_type for p in pieces[7:]} == _ALL_NAMES


def test_reset_mid_bag_starts_fresh() -> None:
    """reset() discards a partial bag; the next 7 calls form a complete bag."""
    factory = BagTetrominoFactory()
    for _ in range(3):
        factory.create_tetromino()
    factory.reset()
    pieces = [factory.create_tetromino() for _ in range(7)]
    assert {p.shape_type for p in pieces} == _ALL_NAMES


def test_reset_on_empty_bag_is_idempotent() -> None:
    """reset() on an already-empty bag does not break subsequent calls."""
    factory = BagTetrominoFactory()
    for _ in range(7):
        factory.create_tetromino()
    factory.reset()
    pieces = [factory.create_tetromino() for _ in range(7)]
    assert {p.shape_type for p in pieces} == _ALL_NAMES
