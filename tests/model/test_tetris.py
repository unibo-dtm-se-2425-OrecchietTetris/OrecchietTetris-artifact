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
    time.sleep(1)
    assert game.is_game_over
    # Thread should have exited on its own (join with generous timeout)
    assert game._game_thread is not None
    game._game_thread.join(timeout=1.0)
    assert not game._game_thread.is_alive()
