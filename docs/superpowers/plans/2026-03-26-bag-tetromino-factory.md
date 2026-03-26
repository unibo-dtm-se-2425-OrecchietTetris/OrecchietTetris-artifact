# Bag Tetromino Factory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace inline `random.choice` tetromino extraction with a Factory Method pattern: an `ITetrominoFactory` interface and a `BagTetrominoFactory` concrete class that implements the 7-bag randomizer algorithm, injected into `Tetris` as a constructor argument.

**Architecture:** `ITetrominoFactory(ABC)` lives in `model/interfaces/` and defines `create_tetromino() -> ITetromino` and `reset() -> None`. `BagTetrominoFactory` holds a `list[ShapeType]` bag; when empty, it refills with all 7 shapes and shuffles before popping the next piece. `Tetris.__init__` accepts an optional `factory: ITetrominoFactory` argument (defaults to `BagTetrominoFactory()`) and calls `reset()` on each `start()`.

**Tech Stack:** Python 3.11+, mypy strict, flake8, pytest. Poetry task runner (`poetry run poe mypy`, `poetry run poe flake8`, `poetry run poe test`).

---

## File Map

| Action | Path |
|--------|------|
| Create | `OrecchietTetris/model/interfaces/itetromino_factory.py` |
| Modify | `OrecchietTetris/model/interfaces/__init__.py` |
| Create | `OrecchietTetris/model/bag_tetromino_factory.py` |
| Modify | `OrecchietTetris/model/__init__.py` |
| Modify | `OrecchietTetris/model/tetris.py` |
| Create | `tests/model/test_bag_tetromino_factory.py` |
| Modify | `tests/model/test_tetris.py` |

---

## Task 1: `ITetrominoFactory` interface

**Files:**
- Create: `OrecchietTetris/model/interfaces/itetromino_factory.py`
- Modify: `OrecchietTetris/model/interfaces/__init__.py`

The interface is an abstract base class — there is no testable behaviour to drive with TDD. Create it, wire it into the package exports, and verify mypy is happy.

- [ ] **Step 1: Create `OrecchietTetris/model/interfaces/itetromino_factory.py`**

```python
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
```

- [ ] **Step 2: Add `ITetrominoFactory` to `OrecchietTetris/model/interfaces/__init__.py`**

Replace the file contents with:

```python
from .itetromino import ITetromino
from .iboard import IBoard
from .itetris import ITetris
from .itetromino_factory import ITetrominoFactory

__all__ = ["IBoard", "ITetris", "ITetromino", "ITetrominoFactory"]
```

- [ ] **Step 3: Run type check**

```bash
poetry run poe mypy
```

Expected: 0 errors.

- [ ] **Step 4: Commit**

```bash
git add OrecchietTetris/model/interfaces/itetromino_factory.py OrecchietTetris/model/interfaces/__init__.py
git commit -m "feat(factory): add ITetrominoFactory interface"
```

---

## Task 2: `BagTetrominoFactory` (TDD)

**Files:**
- Create: `tests/model/test_bag_tetromino_factory.py`
- Create: `OrecchietTetris/model/bag_tetromino_factory.py`
- Modify: `OrecchietTetris/model/__init__.py`

The 7-bag algorithm guarantees every group of 7 pieces contains all 7 shapes exactly once. Tests drive the implementation; run them to confirm they fail before writing the implementation.

- [ ] **Step 1: Create `tests/model/test_bag_tetromino_factory.py`**

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
poetry run pytest tests/model/test_bag_tetromino_factory.py -v
```

Expected: 5 errors — `ModuleNotFoundError: No module named 'OrecchietTetris.model.bag_tetromino_factory'`.

- [ ] **Step 3: Create `OrecchietTetris/model/bag_tetromino_factory.py`**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
poetry run pytest tests/model/test_bag_tetromino_factory.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Add exports to `OrecchietTetris/model/__init__.py`**

Replace the file contents with:

```python
from .tetromino import Tetromino, ShapeType
from .board import Board
from .tetris import Tetris
from .bag_tetromino_factory import BagTetrominoFactory

__all__ = ["Board", "BagTetrominoFactory", "Tetris", "Tetromino", "ShapeType"]
```

- [ ] **Step 6: Run full checks**

```bash
poetry run poe mypy
poetry run poe flake8
poetry run poe test
```

Expected: 0 mypy errors, 0 flake8 errors, all tests pass.

- [ ] **Step 7: Commit**

```bash
git add OrecchietTetris/model/bag_tetromino_factory.py OrecchietTetris/model/__init__.py tests/model/test_bag_tetromino_factory.py
git commit -m "feat(factory): add BagTetrominoFactory with 7-bag algorithm"
```

---

## Task 3: Wire `Tetris` to `ITetrominoFactory`, update `test_tetris.py`

**Files:**
- Modify: `OrecchietTetris/model/tetris.py`
- Modify: `tests/model/test_tetris.py`

`Tetris` is updated to accept an `ITetrominoFactory` and delegate all piece creation to it. Existing tests in `test_tetris.py` currently control piece generation by monkeypatching `random.choice` inside `tetromino.py` — after this change, the factory is the single creation point, so monkeypatching no longer works. Those tests are updated to pass a `FixedTetrominoFactory` test helper instead.

Update tests first (TDD order): the updated tests will fail because `Tetris` doesn't yet accept `factory`; then update `tetris.py` to make them pass.

- [ ] **Step 1: Update `tests/model/test_tetris.py`**

Replace the entire file with:

```python
"""
Unit and integration tests for the Tetris game model.

Unit tests cover individual Tetris methods in isolation (movement, rotation,
hold, shadow, observer events). Integration tests verify Tetris, Board, and
Tetromino working together across multi-step game flows.
"""
from typing import Any, List, Tuple

import pytest

from OrecchietTetris.utils import Observer, EventType
import time

from OrecchietTetris.model.tetris import (
    Tetris,
    BASE_TICK_INTERVAL,
    MIN_TICK_INTERVAL,
)
from OrecchietTetris.model.interfaces import ITetrominoFactory, ITetromino
from OrecchietTetris.model.tetromino import Tetromino, ShapeType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class MockObserver(Observer):
    def __init__(self) -> None:
        self.events: List[Tuple[EventType, Any]] = []

    def update(self, event_type: EventType, data: Any) -> None:
        self.events.append((event_type, data))

    def event_types(self) -> List[EventType]:
        return [e[0] for e in self.events]

    def data_for(self, event_type: EventType) -> Any:
        return next((e[1] for e in self.events if e[0] == event_type), None)


class FixedTetrominoFactory(ITetrominoFactory):
    """Test helper: always produces the same shape type."""

    def __init__(self, shape_type: ShapeType) -> None:
        self._shape_type = shape_type

    def create_tetromino(self) -> ITetromino:
        return Tetromino(self._shape_type)

    def reset(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def observer() -> MockObserver:
    return MockObserver()


@pytest.fixture
def o_game() -> Tetris:
    """A started game in which every spawned piece is an O_SHAPE."""
    game = Tetris(factory=FixedTetrominoFactory(ShapeType.O_SHAPE))
    game.start()
    return game


@pytest.fixture
def i_game() -> Tetris:
    """A started game in which every spawned piece is an I_SHAPE."""
    game = Tetris(factory=FixedTetrominoFactory(ShapeType.I_SHAPE))
    game.start()
    return game


# ---------------------------------------------------------------------------
# Initial state (before start)
# ---------------------------------------------------------------------------

def test_initial_state_before_start() -> None:
    game = Tetris()
    assert not game.is_running
    assert not game.is_paused
    assert not game.is_game_over
    assert game.score == 0
    assert game.level == 1
    assert game.lines_cleared == 0
    assert game.held_piece is None
    assert game.can_hold


# ---------------------------------------------------------------------------
# start()
# ---------------------------------------------------------------------------

def test_start_sets_running(o_game: Tetris) -> None:
    assert o_game.is_running
    assert not o_game.is_paused
    assert not o_game.is_game_over


def test_start_spawns_pieces(o_game: Tetris) -> None:
    assert o_game.current_piece is not None
    assert o_game.next_piece is not None


def test_start_places_piece_at_top(o_game: Tetris) -> None:
    assert o_game.current_row == 0


def test_start_resets_score_and_state() -> None:
    game = Tetris()
    game.start()
    game._score = 500
    game._lines_cleared = 15
    game.start()
    assert game.score == 0
    assert game.lines_cleared == 0
    assert game.held_piece is None
    assert game.can_hold


# ---------------------------------------------------------------------------
# pause() / resume()
# ---------------------------------------------------------------------------

def test_pause_sets_paused(o_game: Tetris) -> None:
    o_game.pause()
    assert o_game.is_paused
    assert not o_game.is_running


def test_pause_before_start_does_nothing() -> None:
    game = Tetris()
    game.pause()
    assert not game.is_paused


def test_resume_clears_paused(o_game: Tetris) -> None:
    o_game.pause()
    o_game.resume()
    assert not o_game.is_paused
    assert o_game.is_running


def test_resume_when_not_paused_does_nothing(o_game: Tetris) -> None:
    o_game.resume()
    assert not o_game.is_paused


def test_double_pause_stays_paused(o_game: Tetris) -> None:
    o_game.pause()
    o_game.pause()  # second call is a no-op (game not running)
    assert o_game.is_paused


# ---------------------------------------------------------------------------
# move_left() / move_right() / move_down()
# ---------------------------------------------------------------------------

def test_move_left_decrements_col(o_game: Tetris) -> None:
    initial_col = o_game.current_col
    assert o_game.move_left()
    assert o_game.current_col == initial_col - 1


def test_move_left_blocked_at_left_wall(o_game: Tetris) -> None:
    while o_game.move_left():
        pass
    assert o_game.current_col == 0
    assert not o_game.move_left()


def test_move_right_increments_col(o_game: Tetris) -> None:
    initial_col = o_game.current_col
    assert o_game.move_right()
    assert o_game.current_col == initial_col + 1


def test_move_right_blocked_at_right_wall(o_game: Tetris) -> None:
    # O piece is 2-wide; rightmost valid col = cols - 2
    while o_game.move_right():
        pass
    assert o_game.current_col == o_game.board.cols - 2
    assert not o_game.move_right()


def test_move_down_increments_row(o_game: Tetris) -> None:
    assert o_game.move_down()
    assert o_game.current_row == 1


def test_move_returns_false_when_not_started() -> None:
    game = Tetris()
    assert not game.move_left()
    assert not game.move_right()
    assert not game.move_down()


def test_move_returns_false_when_paused(o_game: Tetris) -> None:
    o_game.pause()
    assert not o_game.move_left()
    assert not o_game.move_right()
    assert not o_game.move_down()


def test_move_returns_false_when_current_piece_is_none(o_game: Tetris) -> None:
    o_game.board.clear_falling_piece()
    assert not o_game.move_left()
    assert not o_game.move_right()
    assert not o_game.move_down()


# ---------------------------------------------------------------------------
# rotate()
# ---------------------------------------------------------------------------

def test_rotate_changes_shape(i_game: Tetris) -> None:
    assert i_game.current_piece is not None
    original = [row[:] for row in i_game.current_piece.shape]
    assert i_game.rotate()
    assert i_game.current_piece is not None
    assert i_game.current_piece.shape != original


def test_rotate_reverts_when_invalid() -> None:
    """I piece (1×4) at row 17 cannot rotate clockwise: the 4×1 result
    would need rows 17-20, but the board only has 20 rows (0-19)."""
    game = Tetris(factory=FixedTetrominoFactory(ShapeType.I_SHAPE))
    game.start()
    game._board._current_row = 17
    assert game.current_piece is not None
    original_shape = [row[:] for row in game.current_piece.shape]
    assert not game.rotate()
    assert game.current_piece is not None
    assert game.current_piece.shape == original_shape


# ---------------------------------------------------------------------------
# hard_drop()
# ---------------------------------------------------------------------------

def test_hard_drop_lands_at_bottom(o_game: Tetris) -> None:
    o_game.hard_drop()
    # After the drop the piece locks and the next piece spawns at row 0
    assert o_game.current_row == 0


def test_hard_drop_when_not_running_does_nothing() -> None:
    game = Tetris()
    game.hard_drop()  # must not raise


# ---------------------------------------------------------------------------
# shadow_row
# ---------------------------------------------------------------------------

def test_shadow_row_is_below_current_row(o_game: Tetris) -> None:
    assert o_game.shadow_row >= o_game.current_row


def test_shadow_row_before_start_returns_zero() -> None:
    game = Tetris()
    assert game.shadow_row == 0


# ---------------------------------------------------------------------------
# hold()
# ---------------------------------------------------------------------------

def test_hold_stores_current_piece(o_game: Tetris) -> None:
    assert o_game.current_piece is not None
    piece_type = o_game.current_piece.shape_type
    o_game.hold()
    assert o_game.held_piece is not None
    assert o_game.held_piece.shape_type == piece_type


def test_hold_prevents_second_hold(o_game: Tetris) -> None:
    o_game.hold()
    assert not o_game.can_hold
    assert not o_game.hold()


def test_hold_when_not_running_returns_false() -> None:
    game = Tetris()
    assert not game.hold()


def test_hold_full_cycle(o_game: Tetris) -> None:
    """hold → lock (can_hold resets) → hold again."""
    o_game.hold()
    assert not o_game.can_hold
    o_game.hard_drop()   # locks piece, resets can_hold
    assert o_game.can_hold
    assert o_game.hold()


def test_hold_swap_brings_held_piece_back(o_game: Tetris) -> None:
    o_game.hold()
    stored_type = o_game.held_piece.shape_type if o_game.held_piece else None
    o_game._can_hold = True          # simulate a lock
    o_game.hold()                    # swap: old held → current
    assert o_game.current_piece is not None
    assert o_game.current_piece.shape_type == stored_type


def test_hold_new_piece_is_unrotated_after_swap(o_game: Tetris) -> None:
    o_game.hold()
    o_game._can_hold = True
    o_game.hold()
    expected = [list(row) for row in ShapeType.O_SHAPE.value]
    assert o_game.held_piece is not None
    assert o_game.held_piece.shape == expected


# ---------------------------------------------------------------------------
# score / level / lines
# ---------------------------------------------------------------------------

def test_score_starts_at_zero(o_game: Tetris) -> None:
    assert o_game.score == 0


def test_lines_cleared_starts_at_zero(o_game: Tetris) -> None:
    assert o_game.lines_cleared == 0


def test_level_starts_at_one(o_game: Tetris) -> None:
    assert o_game.level == 1


# ---------------------------------------------------------------------------
# Observer notifications
# ---------------------------------------------------------------------------

def test_start_fires_new_piece_event(observer: MockObserver) -> None:
    game = Tetris()
    game.attach(observer)
    game.start()
    assert EventType.NEW_PIECE in observer.event_types()


def test_move_fires_board_updated(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.move_left()
    assert EventType.BOARD_UPDATED in observer.event_types()


def test_rotate_fires_board_updated(i_game: Tetris, observer: MockObserver) -> None:
    i_game.attach(observer)
    i_game.rotate()
    assert EventType.BOARD_UPDATED in observer.event_types()


def test_failed_move_does_not_fire_event(o_game: Tetris, observer: MockObserver) -> None:
    while o_game.move_left():  # reach the wall
        pass
    o_game.attach(observer)
    assert not o_game.move_left()
    assert EventType.BOARD_UPDATED not in observer.event_types()


def test_pause_fires_paused_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.pause()
    assert EventType.PAUSED in observer.event_types()


def test_resume_fires_resumed_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.pause()
    o_game.resume()
    assert EventType.RESUMED in observer.event_types()


def test_hold_fires_hold_updated_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.hold()
    assert EventType.HOLD_UPDATED in observer.event_types()


def test_lines_cleared_fires_event(o_game: Tetris, observer: MockObserver) -> None:
    """Clearing a line must fire LINES_CLEARED and SCORE_UPDATED."""
    o_game.attach(observer)
    # Fill all but the last two cells of row 19 with direct grid writes
    for c in range(o_game.board.cols):
        o_game._board._grid[19][c] = 1
    # Place current piece to trigger clear_lines in _lock_piece
    o_game._board._current_row = 17
    o_game._board._current_col = 0
    o_game._lock_piece()
    assert EventType.LINES_CLEARED in observer.event_types()
    assert EventType.SCORE_UPDATED in observer.event_types()


# ---------------------------------------------------------------------------
# Integration: game over
# ---------------------------------------------------------------------------

def test_game_over_fires_event(observer: MockObserver) -> None:
    game = Tetris()
    game.attach(observer)
    game.start()
    # Block the spawn columns (4-5) at rows 0-1 without filling full rows
    # (full rows would be cleared, unblocking the spawn)
    spawn_col = game.board.cols // 2 - 1
    for r in [0, 1]:
        game._board._grid[r][spawn_col] = 1
        game._board._grid[r][spawn_col + 1] = 1
    # Lock current piece far from spawn to trigger _spawn_piece
    game._board._current_row = 18
    game._board._current_col = 0
    game._lock_piece()
    assert game.is_game_over
    assert not game.is_running
    assert EventType.GAME_OVER in observer.event_types()


def test_game_over_stops_further_actions() -> None:
    game = Tetris()
    game.start()
    spawn_col = game.board.cols // 2 - 1
    for r in [0, 1]:
        game._board._grid[r][spawn_col] = 1
        game._board._grid[r][spawn_col + 1] = 1
    game._board._current_row = 18
    game._board._current_col = 0
    game._lock_piece()
    assert not game.move_left()
    assert not game.move_right()
    assert not game.move_down()
    assert not game.rotate()


# ---------------------------------------------------------------------------
# Integration: hold cycle
# ---------------------------------------------------------------------------

def test_hold_full_cycle_integration(o_game: Tetris) -> None:
    """hold → lock (can_hold resets) → hold again."""
    o_game.hold()
    assert not o_game.can_hold
    o_game.hard_drop()   # locks piece, resets can_hold
    assert o_game.can_hold
    assert o_game.hold()


# ---------------------------------------------------------------------------
# tick_interval
# ---------------------------------------------------------------------------

def test_tick_interval_at_level_1() -> None:
    game = Tetris()
    game.start()
    assert game.tick_interval == BASE_TICK_INTERVAL


def test_tick_interval_decreases_with_level() -> None:
    game = Tetris()
    game.start()
    interval_l1 = game.tick_interval
    game._level = 5
    assert game.tick_interval < interval_l1


def test_tick_interval_does_not_go_below_minimum() -> None:
    game = Tetris()
    game.start()
    game._level = 100
    assert game.tick_interval == MIN_TICK_INTERVAL


# ---------------------------------------------------------------------------
# play() / stop()
# ---------------------------------------------------------------------------

def test_play_starts_the_game() -> None:
    game = Tetris()
    game.play()
    assert game.is_running
    game.stop()


def test_play_resets_score() -> None:
    game = Tetris()
    game.play()
    game._score = 999
    game.play()  # restarts
    assert game.score == 0
    game.stop()


def test_play_spawns_background_thread() -> None:
    game = Tetris()
    game.play()
    assert game._game_thread is not None
    assert game._game_thread.is_alive()
    game.stop()


def test_stop_terminates_thread() -> None:
    game = Tetris()
    game.play()
    game.stop()
    assert game._game_thread is None


def test_stop_when_not_playing_does_not_raise() -> None:
    Tetris().stop()  # must not raise


def test_play_replaces_existing_loop() -> None:
    game = Tetris()
    game.play()
    first_thread = game._game_thread
    game.play()  # must stop old loop and start a new one
    assert game._game_thread is not first_thread
    game.stop()


def test_play_advances_piece_automatically() -> None:
    """The background thread must call tick() and move the piece down."""
    game = Tetris()
    # Override tick_interval via the instance to make the loop very fast
    game.__class__ = type(          # narrow subclass only for this instance
        "_FastTetris",
        (Tetris,),
        {"tick_interval": property(lambda self: 0.01)},
    )
    game.play()
    time.sleep(0.15)   # allow ~15 ticks
    game.stop()
    assert game.current_row > 0


def test_loop_exits_when_game_over() -> None:
    """The background thread must exit on its own once the game is over."""
    game = Tetris()
    game.__class__ = type(
        "_FastTetris",
        (Tetris,),
        {"tick_interval": property(lambda self: 0.01)},
    )
    game.play()
    # Fill the spawn columns to force an immediate game-over on next spawn
    spawn_col = game.board.cols // 2 - 1
    for r in [0, 1]:
        game._board._grid[r][spawn_col] = 1
        game._board._grid[r][spawn_col + 1] = 1
    # Wait long enough for the current piece to lock and trigger game-over
    time.sleep(0.5)
    assert game.is_game_over
    # Thread should have exited on its own (join with generous timeout)
    assert game._game_thread is not None
    game._game_thread.join(timeout=1.0)
    assert not game._game_thread.is_alive()
```

- [ ] **Step 2: Run tests to confirm the updated fixtures fail**

```bash
poetry run pytest tests/model/test_tetris.py -v 2>&1 | head -30
```

Expected: `TypeError: Tetris.__init__() got an unexpected keyword argument 'factory'` (or similar) — confirms the tests correctly drive the implementation.

- [ ] **Step 3: Update `OrecchietTetris/model/tetris.py`**

Replace the entire file with:

```python
import threading
from typing import Optional

from OrecchietTetris.model.interfaces import ITetris, IBoard, ITetromino, ITetrominoFactory
from OrecchietTetris.model.board import Board
from OrecchietTetris.model.tetromino import Tetromino, ShapeType
from OrecchietTetris.model.bag_tetromino_factory import BagTetrominoFactory
from OrecchietTetris.utils import EventType


# Automatic tick loop timing
BASE_TICK_INTERVAL: float = 1.0     # seconds at level 1
MIN_TICK_INTERVAL: float = 0.05     # floor (reached at level 10+)
LEVEL_SPEED_INCREMENT: float = 0.1  # seconds faster per level

# Points awarded per number of lines cleared simultaneously
_LINE_POINTS = {1: 100, 2: 300, 3: 500, 4: 800}


class Tetris(ITetris):
    """Main game model. Exposes all player actions and notifies observers on state changes."""

    def __init__(self, factory: Optional[ITetrominoFactory] = None) -> None:
        super().__init__()
        self._factory: ITetrominoFactory = factory if factory is not None else BagTetrominoFactory()
        self._board: Board = Board()
        self._next_piece: ITetromino = self._factory.create_tetromino()
        self._held_piece: Optional[ITetromino] = None
        self._can_hold: bool = True
        self._score: int = 0
        self._level: int = 1
        self._lines_cleared: int = 0
        self._running: bool = False
        self._paused: bool = False
        self._game_over: bool = False
        self._stop_event: threading.Event = threading.Event()
        self._game_thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------ #
    # Read-only properties                                                 #
    # ------------------------------------------------------------------ #

    @property
    def board(self) -> IBoard:
        return self._board

    @property
    def current_piece(self) -> Optional[ITetromino]:
        return self._board.current_piece

    @property
    def next_piece(self) -> ITetromino:
        return self._next_piece

    @property
    def held_piece(self) -> Optional[ITetromino]:
        return self._held_piece

    @property
    def can_hold(self) -> bool:
        return self._can_hold

    @property
    def shadow_row(self) -> int:
        """Row index where the current piece would land if hard-dropped now."""
        piece = self._board.current_piece
        if piece is None:
            return 0
        row = self._board.current_row
        while self._board.is_valid_position(piece, row + 1, self._board.current_col):
            row += 1
        return row

    @property
    def current_row(self) -> int:
        return self._board.current_row

    @property
    def current_col(self) -> int:
        return self._board.current_col

    @property
    def score(self) -> int:
        return self._score

    @property
    def level(self) -> int:
        return self._level

    @property
    def lines_cleared(self) -> int:
        return self._lines_cleared

    @property
    def is_running(self) -> bool:
        return self._running and not self._paused and not self._game_over

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def is_game_over(self) -> bool:
        return self._game_over

    # ------------------------------------------------------------------ #
    # Game-flow actions                                                    #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        """Reset the game and begin play."""
        self._board.reset()
        self._score = 0
        self._level = 1
        self._lines_cleared = 0
        self._held_piece = None
        self._can_hold = True
        self._game_over = False
        self._paused = False
        self._running = True
        self._factory.reset()
        self._spawn_piece()

    def pause(self) -> None:
        """Pause the game."""
        if self._running and not self._paused and not self._game_over:
            self._paused = True
            self.notify(EventType.PAUSED)

    def resume(self) -> None:
        """Resume a paused game."""
        if self._paused:
            self._paused = False
            self.notify(EventType.RESUMED)

    def tick(self) -> None:
        """Advance the game by one gravity step. Call this on a timer."""
        if self.is_running:
            self.move_down()

    @property
    def tick_interval(self) -> float:
        """Seconds between automatic gravity ticks at the current level."""
        return max(MIN_TICK_INTERVAL, BASE_TICK_INTERVAL - (self._level - 1) * LEVEL_SPEED_INCREMENT)

    def play(self) -> None:
        """Start a fresh game and launch the automatic tick loop.

        Stops any existing loop, resets the game via ``start()``, then spawns
        a daemon thread that calls ``tick()`` every ``tick_interval`` seconds.
        """
        if self._game_thread is not None and self._game_thread.is_alive():
            self.stop()
        self.start()
        self._stop_event.clear()
        self._game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self._game_thread.start()

    def stop(self) -> None:
        """Stop the automatic tick loop. The game state is preserved.

        Signals the background thread to exit and blocks until it finishes
        (up to 2 s). Safe to call even when no loop is running.
        """
        self._stop_event.set()
        if self._game_thread is not None:
            self._game_thread.join(timeout=2.0)
            self._game_thread = None

    def _game_loop(self) -> None:
        """Background thread body: sleeps for ``tick_interval`` then calls ``tick()``.

        Exits when the stop event is set or the game ends naturally.
        Uses ``Event.wait`` instead of ``time.sleep`` so that ``stop()``
        interrupts the sleep immediately.
        """
        while not self._stop_event.is_set() and not self._game_over:
            interrupted = self._stop_event.wait(timeout=self.tick_interval)
            if interrupted:
                break
            self.tick()

    # ------------------------------------------------------------------ #
    # Player actions                                                       #
    # ------------------------------------------------------------------ #

    def move_left(self) -> bool:
        """Shift the current piece one column to the left. Returns True if moved."""
        return self._try_move(self._board.current_row, self._board.current_col - 1)

    def move_right(self) -> bool:
        """Shift the current piece one column to the right. Returns True if moved."""
        return self._try_move(self._board.current_row, self._board.current_col + 1)

    def move_down(self) -> bool:
        """Shift the current piece one row down. Locks and spawns if blocked. Returns True if moved."""
        if not self.is_running:
            return False
        moved = self._try_move(self._board.current_row + 1, self._board.current_col)
        if not moved:
            self._lock_piece()
        return moved

    def rotate(self) -> bool:
        """Rotate the current piece clockwise. Returns True if rotation was applied."""
        if not self.is_running:
            return False
        piece = self._board.current_piece
        if piece is None:
            return False
        piece.rotate()
        if not self._board.is_valid_position(piece, self._board.current_row, self._board.current_col):
            for _ in range(3):
                piece.rotate()
            return False
        self.notify(EventType.BOARD_UPDATED)
        return True

    def hard_drop(self) -> None:
        """Instantly drop the current piece to the lowest valid row and lock it."""
        if not self.is_running:
            return
        self._board.move_falling_piece(self.shadow_row, self._board.current_col)
        self._lock_piece()

    def hold(self) -> bool:
        """Store the current piece in the hold slot (or swap with the held piece).

        The piece is always stored in its original (unrotated) orientation.
        Can only be used once per piece; resets when a piece locks.
        Returns True if the hold was performed.
        """
        if not self.is_running or not self._can_hold:
            return False

        piece = self._board.current_piece
        if piece is None:
            return False
        incoming = self._held_piece
        self._held_piece = Tetromino(ShapeType[piece.shape_type])
        self._can_hold = False
        self.notify(EventType.HOLD_UPDATED, self._held_piece)

        if incoming is None:
            self._spawn_piece()
        else:
            self._spawn_piece(incoming)

        return True

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _try_move(self, new_row: int, new_col: int) -> bool:
        if not self.is_running:
            return False
        piece = self._board.current_piece
        if piece is None:
            return False
        is_valid_move = self._board.move_falling_piece(new_row, new_col)
        if is_valid_move:
            self.notify(EventType.BOARD_UPDATED)
        return is_valid_move

    def _lock_piece(self) -> None:
        """Place the current piece on the board, clear lines, update score, spawn next piece."""
        piece = self._board.current_piece
        if piece is None:
            return
        self._board.place_tetromino(piece, self._board.current_row, self._board.current_col)
        self._board.clear_falling_piece()
        self._can_hold = True
        self.notify(EventType.BOARD_UPDATED)

        cleared = self._board.clear_lines()
        if cleared:
            self._lines_cleared += cleared
            self._level = self._lines_cleared // 10 + 1
            self._score += _LINE_POINTS.get(cleared, 0) * self._level
            self.notify(EventType.LINES_CLEARED, cleared)
            self.notify(EventType.SCORE_UPDATED, self._score)

        self._spawn_piece()

    def _spawn_piece(self, new_piece: Optional[ITetromino] = None) -> None:
        """Promote piece to current, generate a new next piece, check game-over."""
        if new_piece is None:
            new_piece = self._next_piece
            self._next_piece = self._factory.create_tetromino()
        spawn_col = self._board.cols // 2 - 1
        self._board.set_falling_piece(new_piece, 0, spawn_col)

        if self._board.is_game_over(new_piece, spawn_col):
            self._running = False
            self._game_over = True
            self.notify(EventType.GAME_OVER)
        else:
            self.notify(EventType.NEW_PIECE, self._board.current_piece)
            self.notify(EventType.BOARD_UPDATED)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
poetry run pytest tests/model/test_tetris.py -v
```

Expected: all tests pass (same count as before, no monkeypatch failures).

- [ ] **Step 5: Run full checks**

```bash
poetry run poe mypy
poetry run poe flake8
poetry run poe test
```

Expected: 0 mypy errors, 0 flake8 errors, all tests pass.

- [ ] **Step 6: Commit**

```bash
git add OrecchietTetris/model/tetris.py tests/model/test_tetris.py
git commit -m "feat(factory): wire ITetrominoFactory into Tetris, replace monkeypatching in tests"
```
