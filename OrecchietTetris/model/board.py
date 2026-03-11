from typing import Optional

from OrecchietTetris.model.interfaces import IBoard, ITetromino

ROWS = 20
COLS = 10


class Board(IBoard):
    """Manages the fixed grid of placed cells and the currently falling piece."""

    def __init__(self, rows: int = ROWS, cols: int = COLS) -> None:
        self._rows = rows
        self._cols = cols
        self._grid: list[list[int]] = [[0] * cols for _ in range(rows)]
        self._current_piece: Optional[ITetromino] = None
        self._current_row: int = 0
        self._current_col: int = 0

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def current_piece(self) -> Optional[ITetromino]:
        return self._current_piece

    @property
    def current_row(self) -> int:
        return self._current_row

    @property
    def current_col(self) -> int:
        return self._current_col

    @property
    def grid(self) -> list[list[int]]:
        """Read-only snapshot of the fixed grid, including the falling piece."""
        grid = [row[:] for row in self._grid]
        if self._current_piece is not None:
            for r, line in enumerate(self._current_piece.shape):
                for c, cell in enumerate(line):
                    if cell:
                        gr, gc = self._current_row + r, self._current_col + c
                        if 0 <= gr < self._rows and 0 <= gc < self._cols:
                            grid[gr][gc] = cell
        return grid

    def set_falling_piece(self, piece: ITetromino, row: int, col: int) -> None:
        """Set the current falling piece and its position."""
        self._current_piece = piece
        self._current_row = row
        self._current_col = col

    def move_falling_piece(self, row: int, col: int) -> bool:
        """Update the position of the current falling piece."""
        if self._current_piece is None:
            return False
        if self.is_valid_position(self._current_piece, row, col):
            self._current_row = row
            self._current_col = col
            return True
        return False

    def clear_falling_piece(self) -> None:
        """Remove the falling piece reference after locking it into the fixed grid."""
        self._current_piece = None

    def is_valid_position(self, tetromino: ITetromino, row: int, col: int) -> bool:
        """Return True if the tetromino fits at (row, col) without overlap or out-of-bounds."""
        for r, line in enumerate(tetromino.shape):
            for c, cell in enumerate(line):
                if cell:
                    gr, gc = row + r, col + c
                    if gr < 0 or gr >= self._rows or gc < 0 or gc >= self._cols:
                        return False
                    if self._grid[gr][gc]:
                        return False
        return True

    def place_tetromino(self, tetromino: ITetromino, row: int, col: int) -> None:
        """Lock the tetromino into the fixed grid at position (row, col)."""
        for r, line in enumerate(tetromino.shape):
            for c, cell in enumerate(line):
                if cell:
                    self._grid[row + r][col + c] = cell

    def clear_lines(self) -> int:
        """Remove all complete lines and return the number of lines cleared."""
        full_lines = [r for r in range(self._rows) if all(self._grid[r])]
        for r in full_lines:
            del self._grid[r]
            self._grid.insert(0, [0] * self._cols)
        return len(full_lines)

    def is_game_over(self, tetromino: ITetromino, spawn_col: int) -> bool:
        """Return True if the tetromino cannot be placed at the spawn row."""
        return not self.is_valid_position(tetromino, 0, spawn_col)

    def reset(self) -> None:
        """Clear the grid and the falling piece back to empty."""
        self._grid = [[0] * self._cols for _ in range(self._rows)]
        self._current_piece = None
