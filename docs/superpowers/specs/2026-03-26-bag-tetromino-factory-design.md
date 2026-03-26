# Design: Bag Tetromino Factory with Factory Method Pattern

**Date:** 2026-03-26

## Overview

Replace the inline `random.choice` tetromino extraction in `Tetris._spawn_piece` with a Factory Method design pattern. Introduce an abstract `ITetrominoFactory` interface and a concrete `BagTetrominoFactory` that implements the 7-bag randomizer algorithm. `Tetris` accepts the factory as a constructor argument (default `BagTetrominoFactory()`).

## Algorithm: 7-Bag Randomizer

The bag algorithm guarantees that every sequence of 7 pieces contains all 7 tetromino shapes exactly once, in a shuffled order. When the bag empties, a new bag of all 7 shapes is shuffled and dealt. This prevents the long droughts of a single shape that occur with pure random selection.

`reset()` clears the current bag so the next `create_tetromino()` call refills and reshuffles from scratch. `Tetris.start()` calls `reset()` before spawning the first piece.

## Files Added

- `OrecchietTetris/model/interfaces/itetromino_factory.py` — `ITetrominoFactory(ABC)` with two abstract methods: `create_tetromino() -> ITetromino` and `reset() -> None`.
- `OrecchietTetris/model/bag_tetromino_factory.py` — `BagTetrominoFactory(ITetrominoFactory)`: holds a `list[ShapeType]` bag; on `create_tetromino()`, refills and shuffles if empty, then pops and returns a `Tetromino`; `reset()` clears the bag.
- `tests/model/test_bag_tetromino_factory.py` — unit tests for `BagTetrominoFactory` (see Tests section).

## Files Modified

### `OrecchietTetris/model/interfaces/__init__.py`

Export `ITetrominoFactory` alongside existing exports.

### `OrecchietTetris/model/interfaces/itetromino_factory.py` (new)

```python
from abc import ABC, abstractmethod
from OrecchietTetris.model.interfaces.itetromino import ITetromino

class ITetrominoFactory(ABC):
    @abstractmethod
    def create_tetromino(self) -> ITetromino: ...

    @abstractmethod
    def reset(self) -> None: ...
```

### `OrecchietTetris/model/bag_tetromino_factory.py` (new)

```python
import random
from OrecchietTetris.model.interfaces import ITetrominoFactory, ITetromino
from OrecchietTetris.model.tetromino import Tetromino, ShapeType

class BagTetrominoFactory(ITetrominoFactory):
    def __init__(self) -> None:
        self._bag: list[ShapeType] = []

    def create_tetromino(self) -> ITetromino:
        if not self._bag:
            self._bag = list(ShapeType)
            random.shuffle(self._bag)
        return Tetromino(self._bag.pop())

    def reset(self) -> None:
        self._bag = []
```

### `OrecchietTetris/model/tetris.py`

- Import `ITetrominoFactory`, `BagTetrominoFactory`.
- `__init__` signature: add `factory: ITetrominoFactory = BagTetrominoFactory()` as a default-argument parameter; store as `self._factory`.
- `__init__` body: `self._next_piece: ITetromino = self._factory.create_tetromino()` (type widens from `Tetromino` to `ITetromino`).
- `start()`: call `self._factory.reset()` before `self._spawn_piece()`.
- `_spawn_piece()`: replace `self._next_piece = Tetromino()` with `self._next_piece = self._factory.create_tetromino()`.
- `hold()`: unchanged — `Tetromino(ShapeType[piece.shape_type])` is correct here (restoring a known shape, not generating a random one from the queue).

### `OrecchietTetris/model/__init__.py`

Export `BagTetrominoFactory` and `ITetrominoFactory`.

### `tests/model/test_tetris.py`

Replace `o_game` fixture: remove `monkeypatch` of `random.choice`. Instead define a `FixedTetrominoFactory` (local test class returning `Tetromino(ShapeType.O_SHAPE)` on every call, `reset()` is a no-op) and pass it to `Tetris(factory=FixedTetrominoFactory())`.

## Tests

`tests/model/test_bag_tetromino_factory.py`:

- **test_first_bag_contains_all_shapes**: call `create_tetromino()` 7 times; assert the set of `shape_type` values equals the set of all 7 `ShapeType` names.
- **test_first_bag_no_duplicates**: call 7 times; assert the list of shape types has no duplicates.
- **test_second_bag_also_complete**: call 14 times; assert both the first 7 and the second 7 together cover all shape types (each batch of 7 is complete).
- **test_reset_mid_bag_starts_fresh**: call 3 times, then `reset()`, then call 7 times; assert the last 7 form a complete bag.
- **test_reset_on_empty_bag_is_idempotent**: call 7 times to drain, then `reset()`, then call 7 times; assert all 7 shapes present.

## Out of Scope

- Adding new tetromino shapes.
- Lookahead preview of more than one piece.
- Seeded randomness / replay.
