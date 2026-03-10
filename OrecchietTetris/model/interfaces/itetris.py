from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from OrecchietTetris.model.interfaces import IBoard, ITetromino
from OrecchietTetris.utils import Subject


class ITetris(Subject, ABC):
    """Interface for the Tetris game model.

    Inherits from ``Subject`` so that any implementation is automatically
    observable (attach/detach/notify) without redeclaring that inheritance.
    Concrete classes only need to inherit from ``ITetris``.
    """

    # ------------------------------------------------------------------ #
    # Board & piece state                                                  #
    # ------------------------------------------------------------------ #

    @property
    @abstractmethod
    def board(self) -> IBoard:
        """The fixed grid of placed cells."""

    @property
    @abstractmethod
    def current_piece(self) -> ITetromino:
        """The falling piece currently controlled by the player."""

    @property
    @abstractmethod
    def next_piece(self) -> ITetromino:
        """The piece that will spawn after the current one locks."""

    @property
    @abstractmethod
    def held_piece(self) -> Optional[ITetromino]:
        """The piece stored in the hold slot, or *None* if the slot is empty."""

    @property
    @abstractmethod
    def can_hold(self) -> bool:
        """False after a hold has been used; resets to True when a piece locks."""

    @property
    @abstractmethod
    def shadow_row(self) -> int:
        """Row index where the current piece would land if hard-dropped now."""

    @property
    @abstractmethod
    def current_row(self) -> int:
        """Current top row of the falling piece."""

    @property
    @abstractmethod
    def current_col(self) -> int:
        """Current left column of the falling piece."""

    # ------------------------------------------------------------------ #
    # Score / progression                                                  #
    # ------------------------------------------------------------------ #

    @property
    @abstractmethod
    def score(self) -> int:
        """Accumulated score."""

    @property
    @abstractmethod
    def level(self) -> int:
        """Current level (increases every 10 lines cleared)."""

    @property
    @abstractmethod
    def lines_cleared(self) -> int:
        """Total number of lines cleared since the game started."""

    # ------------------------------------------------------------------ #
    # Game state flags                                                     #
    # ------------------------------------------------------------------ #

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """True when the game is active (not paused, not over)."""

    @property
    @abstractmethod
    def is_paused(self) -> bool:
        """True when the game is paused."""

    @property
    @abstractmethod
    def is_game_over(self) -> bool:
        """True when the game has ended."""

    # ------------------------------------------------------------------ #
    # Game-flow actions                                                    #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def start(self) -> None:
        """Reset and start a new game."""

    @abstractmethod
    def pause(self) -> None:
        """Pause the running game."""

    @abstractmethod
    def resume(self) -> None:
        """Resume a paused game."""

    @abstractmethod
    def tick(self) -> None:
        """Advance gravity by one step (call this on a timer)."""

    # ------------------------------------------------------------------ #
    # Player actions                                                       #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def move_left(self) -> bool:
        """Shift the current piece one column left. Returns True if moved."""

    @abstractmethod
    def move_right(self) -> bool:
        """Shift the current piece one column right. Returns True if moved."""

    @abstractmethod
    def move_down(self) -> bool:
        """Shift the current piece one row down; locks if blocked. Returns True if moved."""

    @abstractmethod
    def rotate(self) -> bool:
        """Rotate the current piece clockwise; reverts if the rotation is invalid. Returns True if applied."""

    @abstractmethod
    def hard_drop(self) -> None:
        """Instantly drop the current piece to the lowest valid row and lock it."""

    @abstractmethod
    def hold(self) -> bool:
        """Store the current piece in the hold slot (or swap with the held piece).

        Rules:
        - Can only be used once per piece; resets when a piece locks.
        - The stored piece is always kept in its original (unrotated) orientation.
        Returns True if the hold was performed.
        """

    # ------------------------------------------------------------------ #
    # Automatic game loop                                                  #
    # ------------------------------------------------------------------ #

    @property
    @abstractmethod
    def tick_interval(self) -> float:
        """Seconds between automatic gravity ticks at the current level.

        Starts at ``BASE_TICK_INTERVAL`` (level 1) and shrinks by 0.1 s per
        level, down to a minimum of ``MIN_TICK_INTERVAL``.
        """

    @abstractmethod
    def play(self) -> None:
        """Start a fresh game and launch the automatic tick loop.

        Internally calls ``start()`` and spawns a daemon thread that fires
        ``tick()`` every ``tick_interval`` seconds. If a loop is already
        running it is stopped first, so ``play()`` always begins a clean game.
        """

    @abstractmethod
    def stop(self) -> None:
        """Stop the automatic tick loop. The game state is preserved.

        Signals the background thread to exit and waits for it to finish.
        Safe to call even if the loop is not running.
        """
