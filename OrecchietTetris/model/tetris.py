import threading
from typing import Optional

from OrecchietTetris.model.interfaces import ITetris, IBoard, ITetromino
from OrecchietTetris.model.board import Board
from OrecchietTetris.model.tetromino import Tetromino, ShapeType
from OrecchietTetris.utils import EventType


# Automatic tick loop timing
BASE_TICK_INTERVAL: float = 1.0     # seconds at level 1
MIN_TICK_INTERVAL: float = 0.05     # floor (reached at level 10+)
LEVEL_SPEED_INCREMENT: float = 0.1  # seconds faster per level

# Points awarded per number of lines cleared simultaneously
_LINE_POINTS = {1: 100, 2: 300, 3: 500, 4: 800}


class Tetris(ITetris):
    """Main game model. Exposes all player actions and notifies observers on state changes."""

    def __init__(self) -> None:
        super().__init__()
        self._board: Board = Board()
        self._next_piece: Tetromino = Tetromino()
        self._held_piece: Optional[Tetromino] = None
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
            spawn_col = self._board.cols // 2 - 1
            self._board.set_falling_piece(incoming, 0, spawn_col)
            if self._board.is_game_over(incoming, spawn_col):
                self._running = False
                self._game_over = True
                self.notify(EventType.GAME_OVER)
            else:
                self.notify(EventType.NEW_PIECE, self._board.current_piece)
                self.notify(EventType.BOARD_UPDATED)

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
        if self._board.is_valid_position(piece, new_row, new_col):
            self._board.move_falling_piece(new_row, new_col)
            self.notify(EventType.BOARD_UPDATED)
            return True
        return False

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

    def _spawn_piece(self) -> None:
        """Promote next piece to current, generate a new next piece, check game-over."""
        new_piece = self._next_piece
        self._next_piece = Tetromino()
        spawn_col = self._board.cols // 2 - 1
        self._board.set_falling_piece(new_piece, 0, spawn_col)

        if self._board.is_game_over(new_piece, spawn_col):
            self._running = False
            self._game_over = True
            self.notify(EventType.GAME_OVER)
        else:
            self.notify(EventType.NEW_PIECE, self._board.current_piece)
            self.notify(EventType.BOARD_UPDATED)
