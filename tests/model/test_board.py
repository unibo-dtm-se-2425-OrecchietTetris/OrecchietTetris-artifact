import pytest

from OrecchietTetris.model.board import Board
from OrecchietTetris.model.tetromino import Tetromino, ShapeType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def board() -> Board:
    return Board()


@pytest.fixture
def small_board() -> Board:
    """4×4 board that makes collision and line-clearing tests easy to reason about."""
    return Board(rows=4, cols=4)


@pytest.fixture
def o_piece() -> Tetromino:
    return Tetromino(ShapeType.O_SHAPE)


@pytest.fixture
def i_piece() -> Tetromino:
    return Tetromino(ShapeType.I_SHAPE)


# ---------------------------------------------------------------------------
# Dimensions & initial state
# ---------------------------------------------------------------------------


def test_custom_dimensions() -> None:
    b = Board(rows=4, cols=6)
    assert b.rows == 4
    assert b.cols == 6


def test_grid_initially_empty(board: Board) -> None:
    assert all(cell == 0 for row in board.grid for cell in row)


def test_grid_has_correct_size(board: Board) -> None:
    grid = board.grid
    assert len(grid) == board.rows
    assert all(len(row) == board.cols for row in grid)


def test_grid_returns_copy(board: Board, o_piece: Tetromino) -> None:
    """Mutating the returned grid must not affect the board's internal state."""
    snapshot = board.grid
    snapshot[0][0] = 99
    assert board.grid[0][0] == 0


# ---------------------------------------------------------------------------
# is_valid_position
# ---------------------------------------------------------------------------

def test_is_valid_position_top_left(board: Board, o_piece: Tetromino) -> None:
    assert board.is_valid_position(o_piece, 0, 0)


def test_is_valid_position_top_right(board: Board, o_piece: Tetromino) -> None:
    # O is 2-wide; rightmost valid col = cols - 2 = 8
    assert board.is_valid_position(o_piece, 0, board.cols - 2)


def test_is_valid_position_bottom_left(board: Board, o_piece: Tetromino) -> None:
    # O is 2-tall; lowest valid top row = rows - 2 = 18
    assert board.is_valid_position(o_piece, board.rows - 2, 0)


def test_is_valid_position_out_of_bounds_right(board: Board, o_piece: Tetromino) -> None:
    # O at col cols-1 would occupy cols (cols-1) and cols → out of bounds
    assert not board.is_valid_position(o_piece, 0, board.cols - 1)


def test_is_valid_position_out_of_bounds_left(board: Board, o_piece: Tetromino) -> None:
    assert not board.is_valid_position(o_piece, 0, -1)


def test_is_valid_position_out_of_bounds_bottom(board: Board, o_piece: Tetromino) -> None:
    # O at the last row would need row rows and rows+1 → out of bounds
    assert not board.is_valid_position(o_piece, board.rows - 1, 0)


def test_is_valid_position_above_board(board: Board, o_piece: Tetromino) -> None:
    assert not board.is_valid_position(o_piece, -1, 0)


def test_is_valid_position_overlap(small_board: Board, o_piece: Tetromino) -> None:
    small_board.place_tetromino(o_piece, 0, 0)
    assert not small_board.is_valid_position(Tetromino(ShapeType.O_SHAPE), 0, 0)


def test_is_valid_position_adjacent_no_overlap(small_board: Board, o_piece: Tetromino) -> None:
    small_board.place_tetromino(o_piece, 0, 0)
    assert small_board.is_valid_position(Tetromino(ShapeType.O_SHAPE), 0, 2)


def test_is_valid_position_i_shape_fits(board: Board, i_piece: Tetromino) -> None:
    # I is 1×4; rightmost valid col = cols - 4 = 6
    assert board.is_valid_position(i_piece, 0, 6)
    assert not board.is_valid_position(i_piece, 0, 7)


# ---------------------------------------------------------------------------
# place_tetromino
# ---------------------------------------------------------------------------

def test_place_o_shape_fills_correct_cells(board: Board, o_piece: Tetromino) -> None:
    board.place_tetromino(o_piece, 0, 0)
    grid = board.grid
    assert grid[0][0] == 2
    assert grid[0][1] == 2
    assert grid[1][0] == 2
    assert grid[1][1] == 2


def test_place_o_shape_does_not_fill_adjacent_cells(board: Board, o_piece: Tetromino) -> None:
    board.place_tetromino(o_piece, 0, 0)
    grid = board.grid
    assert grid[0][2] == 0
    assert grid[2][0] == 0


def test_place_i_shape_fills_row(board: Board, i_piece: Tetromino) -> None:
    board.place_tetromino(i_piece, 0, 0)
    grid = board.grid
    assert all(grid[0][c] == 1 for c in range(4))
    assert grid[1][0] == 0   # row below untouched


def test_place_tetromino_offset_position(board: Board, o_piece: Tetromino) -> None:
    board.place_tetromino(o_piece, 5, 3)
    grid = board.grid
    assert grid[5][3] == 2
    assert grid[5][4] == 2
    assert grid[6][3] == 2
    assert grid[6][4] == 2
    assert grid[4][3] == 0


# ---------------------------------------------------------------------------
# clear_lines
# ---------------------------------------------------------------------------

def test_clear_lines_no_full_rows(small_board: Board, o_piece: Tetromino) -> None:
    # O at (0,0) on 4-col board fills only cols 0-1 → rows not complete
    small_board.place_tetromino(o_piece, 0, 0)
    assert small_board.clear_lines() == []


def test_clear_lines_one_full_row_returns_count(small_board: Board) -> None:
    # I_SHAPE is 1×4 — exactly fills one row of the 4-col board
    small_board.place_tetromino(Tetromino(ShapeType.I_SHAPE), 0, 0)
    assert len(small_board.clear_lines()) == 1


def test_clear_lines_two_full_rows_returns_count(small_board: Board) -> None:
    # Two side-by-side O pieces fill rows 0 and 1 completely on a 4-col board
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 0)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 2)
    assert len(small_board.clear_lines()) == 2


def test_clear_lines_clears_only_full_rows(small_board: Board) -> None:
    # Fill rows 2-3 completely; leave rows 0-1 partial
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 2, 0)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 2, 2)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 0)  # partial (cols 2-3 empty)
    assert len(small_board.clear_lines()) == 2


def test_clear_lines_drops_remaining_rows(small_board: Board) -> None:
    # Fill rows 2-3 completely; put a partial piece at rows 0-1
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 2, 0)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 2, 2)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 0)  # cols 0-1
    small_board.clear_lines()
    grid = small_board.grid
    # Cleared rows push the partial piece down to rows 2-3
    assert grid[2][0] == 2
    assert grid[2][1] == 2
    assert grid[3][0] == 2
    assert grid[3][1] == 2
    # Top two rows now empty
    assert all(grid[0][c] == 0 for c in range(4))
    assert all(grid[1][c] == 0 for c in range(4))


def test_clear_lines_grid_is_empty_afterwards(small_board: Board) -> None:
    # Fill everything → all cleared → grid back to all zeros
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 0)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 2)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 2, 0)
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 2, 2)
    cleared = small_board.clear_lines()
    assert len(cleared) == 4
    assert all(cell == 0 for row in small_board.grid for cell in row)


# ---------------------------------------------------------------------------
# is_game_over
# ---------------------------------------------------------------------------

def test_is_game_over_when_spawn_is_blocked(small_board: Board) -> None:
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 0)
    assert small_board.is_game_over(Tetromino(ShapeType.O_SHAPE), spawn_col=0)


def test_is_not_game_over_when_spawn_is_free(small_board: Board) -> None:
    assert not small_board.is_game_over(Tetromino(ShapeType.O_SHAPE), spawn_col=0)


def test_is_not_game_over_when_spawn_col_is_clear(small_board: Board) -> None:
    # Fill cols 0-1 but not 2-3; spawn at col 2 must be free
    small_board.place_tetromino(Tetromino(ShapeType.O_SHAPE), 0, 0)
    assert not small_board.is_game_over(Tetromino(ShapeType.O_SHAPE), spawn_col=2)


# ---------------------------------------------------------------------------
# reset
# ---------------------------------------------------------------------------

def test_reset_clears_all_cells(board: Board, o_piece: Tetromino) -> None:
    board.place_tetromino(o_piece, 0, 0)
    board.reset()
    assert all(cell == 0 for row in board.grid for cell in row)


def test_reset_preserves_dimensions(board: Board) -> None:
    board.reset()
    assert board.rows == 20
    assert board.cols == 10


def test_reset_allows_placement_again(board: Board, o_piece: Tetromino) -> None:
    board.place_tetromino(o_piece, 0, 0)
    board.reset()
    assert board.is_valid_position(Tetromino(ShapeType.O_SHAPE), 0, 0)


# ---------------------------------------------------------------------------
# Falling piece: set / move / clear
# ---------------------------------------------------------------------------

def test_falling_piece_initially_none(board: Board) -> None:
    assert board.current_piece is None


def test_set_falling_piece_updates_properties(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 3, 4)
    assert board.current_piece is o_piece
    assert board.current_row == 3
    assert board.current_col == 4


def test_move_falling_piece_updates_position(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 0, 0)
    moved = board.move_falling_piece(5, 7)
    assert moved
    assert board.current_row == 5
    assert board.current_col == 7
    assert board.current_piece is o_piece


def test_move_when_current_piece_is_none(board: Board) -> None:
    moved = board.move_falling_piece(5, 7)
    assert not moved
    assert board.current_piece is None
    assert board.current_row == 0
    assert board.current_col == 0


def test_clear_falling_piece_removes_piece(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 0, 0)
    board.clear_falling_piece()
    assert board.current_piece is None


# ---------------------------------------------------------------------------
# Falling piece appears in grid snapshot
# ---------------------------------------------------------------------------

def test_grid_includes_falling_piece(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 5, 3)
    grid = board.grid
    # O piece occupies a 2×2 block
    assert grid[5][3] == 2
    assert grid[5][4] == 2
    assert grid[6][3] == 2
    assert grid[6][4] == 2


def test_grid_falling_piece_does_not_mutate_fixed_grid(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 0, 0)
    _ = board.grid  # take snapshot
    board.clear_falling_piece()
    # Fixed grid must still be empty
    assert all(cell == 0 for row in board._grid for cell in row)


def test_grid_without_falling_piece_is_empty(board: Board) -> None:
    assert all(cell == 0 for row in board.grid for cell in row)


def test_grid_after_clear_falling_piece_excludes_it(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 0, 0)
    board.clear_falling_piece()
    assert all(cell == 0 for row in board.grid for cell in row)


def test_reset_clears_falling_piece(board: Board, o_piece: Tetromino) -> None:
    board.set_falling_piece(o_piece, 2, 2)
    board.reset()
    assert board.current_piece is None
    assert all(cell == 0 for row in board.grid for cell in row)
