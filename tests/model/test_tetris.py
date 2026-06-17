"""
Unit and integration tests for the Tetris game model.

Unit tests cover individual Tetris methods in isolation (movement, rotation,
hold, shadow, observer events). Integration tests verify Tetris, Board, and
Tetromino working together across multi-step game flows.
"""
from typing import Any, List, Tuple

import pytest

from OrecchietTetris.utils import Observer, EventType

from OrecchietTetris.model.tetris import (Tetris)
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


def test_two_lines_cleared_simultaneously(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    for r in [18, 19]:
        for c in range(8):
            o_game._board._grid[r][c] = 1
    o_game._board._current_row = 18
    o_game._board._current_col = 8
    o_game._lock_piece()
    cleared_rows, _ = observer.data_for(EventType.LINES_CLEARED)
    assert len(cleared_rows) == 2


def test_score_increases_after_line_clear(o_game: Tetris) -> None:
    for r in [18, 19]:
        for c in range(8):
            o_game._board._grid[r][c] = 1
    o_game._board._current_row = 18
    o_game._board._current_col = 8
    o_game._lock_piece()
    assert o_game.score > 0


def test_score_scales_with_level(o_game: Tetris) -> None:
    # Set lines_cleared to 20 so the engine computes level = 3 after clearing 2 more
    o_game._lines_cleared = 20
    for r in [18, 19]:
        for c in range(8):
            o_game._board._grid[r][c] = 1
    o_game._board._current_row = 18
    o_game._board._current_col = 8
    o_game._lock_piece()
    # 2 lines at level 3: 300 * 3 = 900
    assert o_game.score == 900


def test_level_increases_every_ten_lines(o_game: Tetris) -> None:
    o_game._lines_cleared = 9
    for r in [18, 19]:
        for c in range(8):
            o_game._board._grid[r][c] = 1
    o_game._board._current_row = 18
    o_game._board._current_col = 8
    o_game._lock_piece()
    # 9 + 2 = 11 lines → level = 11 // 10 + 1 = 2
    assert o_game.level == 2


def test_cleared_rows_are_removed_from_board(o_game: Tetris) -> None:
    for r in [18, 19]:
        for c in range(8):
            o_game._board._grid[r][c] = 1
    o_game._board._current_row = 18
    o_game._board._current_col = 8
    o_game._lock_piece()
    grid = o_game.board.grid
    # Rows 18 and 19 were cleared; they must now be empty
    assert all(grid[18][c] == 0 for c in range(o_game.board.cols))
    assert all(grid[19][c] == 0 for c in range(o_game.board.cols))


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
    assert game.tick_interval == 1


def test_tick_interval_decreases_with_level() -> None:
    game = Tetris()
    game.start()
    interval_l1 = game.tick_interval
    game._level = 5
    assert game.tick_interval < interval_l1


# ---------------------------------------------------------------------------
# tick() drives gravity (the view owns the timer; the model just advances)
# ---------------------------------------------------------------------------

def test_tick_advances_the_piece_one_row() -> None:
    game = Tetris()
    game.start()
    start_row = game.current_row
    game.tick()
    assert game.current_row == start_row + 1


def test_tick_is_a_noop_when_not_running() -> None:
    game = Tetris()  # never started → not running
    game.tick()  # must not raise
    assert not game.is_running


# ---------------------------------------------------------------------------
# Missing coverage: lines 207, 214, 240
# ---------------------------------------------------------------------------

def test_rotate_returns_false_when_current_piece_is_none() -> None:
    """rotate() must return False when the board has no current piece (line 207).

    This edge case can occur if the model is in a running state but the board's
    piece reference is cleared before the call.
    """
    game = Tetris()
    game.start()
    # Force the board into the 'no current piece' state while the game is live
    game._board._current_piece = None
    result = game.rotate()
    assert result is False


def test_rotate_applies_wall_kick_with_nonzero_column_offset() -> None:
    """When the rotated position at offset=0 is blocked, rotate() must try
    adjacent columns and call move_falling_piece() with the offset column (line 214).
    """
    game = Tetris(factory=FixedTetrominoFactory(ShapeType.I_SHAPE))
    game.start()

    # Intercept is_valid_position: reject offset=0 (first call), accept offset=-1 (second)
    call_count: list[int] = [0]
    move_calls: list[tuple[int, int]] = []
    original_move = game._board.move_falling_piece

    def patched_is_valid(piece: Any, row: int, col: int) -> bool:
        call_count[0] += 1
        return call_count[0] > 1  # first call False, rest True

    def patched_move(row: int, col: int) -> None:
        move_calls.append((row, col))
        original_move(row, col)

    game._board.is_valid_position = patched_is_valid  # type: ignore[assignment]
    game._board.move_falling_piece = patched_move  # type: ignore[assignment]

    result = game.rotate()

    assert result is True
    # move_falling_piece must have been called exactly once (the wall-kick path)
    assert len(move_calls) == 1


def test_hold_returns_false_when_current_piece_is_none() -> None:
    """hold() must return False when the board has no current piece (line 240).

    Same edge case as rotate(): board piece is cleared while game is running.
    """
    game = Tetris()
    game.start()
    game._board._current_piece = None
    result = game.hold()
    assert result is False
