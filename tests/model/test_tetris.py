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
from OrecchietTetris.model.tetromino import ShapeType


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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def observer() -> MockObserver:
    return MockObserver()


@pytest.fixture
def o_game(monkeypatch: pytest.MonkeyPatch) -> Tetris:
    """A started game in which every spawned piece is an O_SHAPE."""
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.start()
    return game


@pytest.fixture
def i_game(monkeypatch: pytest.MonkeyPatch) -> Tetris:
    """A started game in which every spawned piece is an I_SHAPE."""
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.I_SHAPE,
    )
    game = Tetris()
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


def test_start_resets_score_and_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
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


def test_rotate_reverts_when_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """I piece (1×4) at row 17 cannot rotate clockwise: the 4×1 result
    would need rows 17-20, but the board only has 20 rows (0-19)."""
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.I_SHAPE,
    )
    game = Tetris()
    game.start()
    game._board._current_row = 17
    assert game.current_piece is not None
    original_shape = [row[:] for row in game.current_piece.shape]
    assert not game.rotate()
    assert game.current_piece is not None
    assert game.current_piece.shape == original_shape


def test_no_rotate_when_current_piece_is_none() -> None:
    game = Tetris()
    game.start()
    game.board.clear_falling_piece()
    assert not game.rotate()


def test_rotate_returns_false_when_not_started() -> None:
    assert not Tetris().rotate()


def test_rotate_returns_false_when_paused(i_game: Tetris) -> None:
    i_game.pause()
    assert not i_game.rotate()


# ---------------------------------------------------------------------------
# shadow_row
# ---------------------------------------------------------------------------


def test_shadow_on_current_piece_none(o_game: Tetris) -> None:
    o_game.board.clear_falling_piece()
    assert o_game.shadow_row == 0


def test_shadow_row_on_empty_board(o_game: Tetris) -> None:
    # O is 2-tall; last valid top row on a 20-row board = 18
    assert o_game.shadow_row == o_game.board.rows - 2


def test_shadow_row_above_filled_rows(o_game: Tetris) -> None:
    # Fill rows 18 and 19 completely (test setup via internal grid)
    for col in range(o_game.board.cols):
        o_game._board._grid[18][col] = 1
        o_game._board._grid[19][col] = 1
    # O piece now lands at row 16 (occupies 16 and 17, above the filled rows)
    assert o_game.shadow_row == 16


def test_shadow_row_equals_current_row_when_immediately_blocked(o_game: Tetris) -> None:
    # Fill row 1 completely → O at row 0 cannot go down at all
    for col in range(o_game.board.cols):
        o_game._board._grid[1][col] = 1
    assert o_game.shadow_row == 0


# ---------------------------------------------------------------------------
# hard_drop()
# ---------------------------------------------------------------------------

def test_hard_drop_fills_board_at_shadow_row(o_game: Tetris) -> None:
    expected_row = o_game.shadow_row
    expected_col = o_game.current_col
    o_game.hard_drop()
    grid = o_game.board.grid
    assert grid[expected_row][expected_col] == 2
    assert grid[expected_row][expected_col + 1] == 2


def test_no_hard_drop_when_current_piece_is_none(o_game: Tetris) -> None:
    o_game.board.move_falling_piece(2, 0)
    o_game.board.clear_falling_piece()
    o_game.hard_drop()
    assert o_game.board.current_row == 2
    assert o_game.current_piece is None


def test_hard_drop_spawns_new_piece(o_game: Tetris) -> None:
    o_game.hard_drop()
    assert o_game.current_row == 0
    assert not o_game.is_game_over


def test_hard_drop_when_not_started_does_nothing() -> None:
    Tetris().hard_drop()  # must not raise


# ---------------------------------------------------------------------------
# hold()
# ---------------------------------------------------------------------------

def test_hold_first_use_stores_piece(o_game: Tetris) -> None:
    assert o_game.current_piece is not None
    piece_type = o_game.current_piece.shape_type
    assert o_game.hold()
    assert o_game.held_piece is not None
    assert o_game.held_piece.shape_type == piece_type


def test_hold_first_use_spawns_new_piece(o_game: Tetris) -> None:
    o_game.hold()
    assert o_game.current_row == 0


def test_cannot_hold_when_current_piece_is_none(o_game: Tetris) -> None:
    o_game.board.clear_falling_piece()
    assert not o_game.hold()
    assert o_game.held_piece is None


def test_game_over_on_hold(o_game: Tetris) -> None:
    o_game.hold()
    spawn_col = o_game.board.cols // 2 - 1
    for r in [0, 1]:
        o_game._board._grid[r][spawn_col] = 1
        o_game._board._grid[r][spawn_col + 1] = 1
    # Lock current piece far from spawn to trigger _spawn_piece
    o_game._board._current_row = 18
    o_game._board._current_col = 0
    o_game._lock_piece()
    assert o_game.is_game_over
    assert not o_game.is_running


def test_hold_stores_piece_in_original_orientation(o_game: Tetris) -> None:
    expected_shape = [list(row) for row in ShapeType.O_SHAPE.value]
    o_game.hold()
    assert o_game.held_piece is not None
    assert o_game.held_piece.shape == expected_shape


def test_hold_disables_can_hold(o_game: Tetris) -> None:
    o_game.hold()
    assert not o_game.can_hold


def test_hold_blocked_when_already_used(o_game: Tetris) -> None:
    o_game.hold()
    assert not o_game.hold()


def test_hold_second_use_swaps_pieces(o_game: Tetris) -> None:
    o_game.hold()
    # Manually re-enable hold to simulate a new piece having locked
    o_game._can_hold = True
    assert o_game.hold()
    assert o_game.held_piece is not None
    assert not o_game.can_hold
    assert o_game.current_row == 0


def test_hold_resets_can_hold_after_lock(o_game: Tetris) -> None:
    o_game.hold()
    assert not o_game.can_hold
    o_game._lock_piece()
    assert o_game.can_hold


def test_hold_when_not_started_returns_false() -> None:
    assert not Tetris().hold()


# ---------------------------------------------------------------------------
# tick()
# ---------------------------------------------------------------------------

def test_tick_moves_piece_down(o_game: Tetris) -> None:
    initial_row = o_game.current_row
    o_game.tick()
    assert o_game.current_row == initial_row + 1


def test_tick_does_nothing_when_paused(o_game: Tetris) -> None:
    initial_row = o_game.current_row
    o_game.pause()
    o_game.tick()
    assert o_game.current_row == initial_row


def test_tick_does_nothing_when_not_started() -> None:
    Tetris().tick()  # must not raise


# ---------------------------------------------------------------------------
# Observer notifications
# ---------------------------------------------------------------------------

def test_start_fires_new_piece_event(monkeypatch: pytest.MonkeyPatch, observer: MockObserver) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
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
    o_game.move_left()  # blocked — no event expected
    assert EventType.BOARD_UPDATED not in observer.event_types()


def test_pause_fires_paused_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.pause()
    assert EventType.PAUSED in observer.event_types()


def test_resume_fires_resumed_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.pause()
    o_game.attach(observer)
    o_game.resume()
    assert EventType.RESUMED in observer.event_types()


def test_hold_fires_hold_updated_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.hold()
    assert EventType.HOLD_UPDATED in observer.event_types()
    assert observer.data_for(EventType.HOLD_UPDATED) is not None


def test_hard_drop_fires_board_updated(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.hard_drop()
    assert EventType.BOARD_UPDATED in observer.event_types()


def test_detached_observer_does_not_receive_event(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    o_game.hard_drop()
    assert EventType.BOARD_UPDATED in observer.event_types()
    o_game.detach(observer)
    observer.events = []
    o_game.hard_drop()
    assert EventType.BOARD_UPDATED not in observer.event_types()


# ---------------------------------------------------------------------------
# Integration: piece locking and spawning
# ---------------------------------------------------------------------------

def test_piece_locks_when_move_down_blocked(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    # Drive piece to the bottom
    while o_game.move_down():
        pass
    # move_down blocked → piece locked → new piece spawned
    assert o_game.current_row == 0
    assert EventType.NEW_PIECE in observer.event_types()


def test_hard_drop_locks_and_new_piece_spawns(o_game: Tetris) -> None:
    o_game.hard_drop()
    assert o_game.current_row == 0
    assert not o_game.is_game_over


def test_multiple_pieces_stack(o_game: Tetris) -> None:
    shadow_first = o_game.shadow_row
    o_game.hard_drop()
    # Second piece shadow must be above the first
    assert o_game.shadow_row < shadow_first


# ---------------------------------------------------------------------------
# Integration: line clearing and scoring
# ---------------------------------------------------------------------------

def test_line_clear_fires_events(o_game: Tetris, observer: MockObserver) -> None:
    o_game.attach(observer)
    # Fill cols 0-7 of rows 18-19; drop O into cols 8-9 to complete both rows
    for r in [18, 19]:
        for c in range(8):
            o_game._board._grid[r][c] = 1
    o_game._board._current_row = 18
    o_game._board._current_col = 8
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
    assert len(observer.data_for(EventType.LINES_CLEARED)) == 2


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

def test_game_over_fires_event(monkeypatch: pytest.MonkeyPatch, observer: MockObserver) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
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


def test_game_over_stops_further_actions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
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
# tick_interval
# ---------------------------------------------------------------------------

def test_tick_interval_at_level_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.start()
    assert game.tick_interval == BASE_TICK_INTERVAL


def test_tick_interval_decreases_with_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.start()
    interval_l1 = game.tick_interval
    game._level = 5
    assert game.tick_interval < interval_l1


def test_tick_interval_does_not_go_below_minimum(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.start()
    game._level = 100
    assert game.tick_interval == MIN_TICK_INTERVAL


# ---------------------------------------------------------------------------
# play() / stop()
# ---------------------------------------------------------------------------

def test_play_starts_the_game(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.play()
    assert game.is_running
    game.stop()


def test_play_resets_score(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.play()
    game._score = 999
    game.play()  # restarts
    assert game.score == 0
    game.stop()


def test_play_spawns_background_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.play()
    assert game._game_thread is not None
    assert game._game_thread.is_alive()
    game.stop()


def test_stop_terminates_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.play()
    game.stop()
    assert game._game_thread is None


def test_stop_when_not_playing_does_not_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    Tetris().stop()  # must not raise


def test_play_replaces_existing_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
    game = Tetris()
    game.play()
    first_thread = game._game_thread
    game.play()  # must stop old loop and start a new one
    assert game._game_thread is not first_thread
    game.stop()


def test_play_advances_piece_automatically(monkeypatch: pytest.MonkeyPatch) -> None:
    """The background thread must call tick() and move the piece down."""
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
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


def test_loop_exits_when_game_over(monkeypatch: pytest.MonkeyPatch) -> None:
    """The background thread must exit on its own once the game is over."""
    monkeypatch.setattr(
        "OrecchietTetris.model.tetromino.random.choice",
        lambda _: ShapeType.O_SHAPE,
    )
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
