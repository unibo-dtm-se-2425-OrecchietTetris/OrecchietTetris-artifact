from __future__ import annotations

from typing import Any, Callable, Optional

from kivy.uix.anchorlayout import AnchorLayout  # type: ignore[import-untyped]
from kivy.uix.gridlayout import GridLayout  # type: ignore[import-untyped]
from kivy.graphics import Color, Line  # type: ignore[import-untyped]
from kivy.clock import Clock  # type: ignore[import-untyped]

from OrecchietTetris.view.block_renderer import BlockRenderer, BLOCK_COLOURS
from OrecchietTetris.view.widgets.cell import Cell
from OrecchietTetris.model.interfaces import ITetromino

BOARD_ROWS: int = 20
BOARD_COLS: int = 10
BOARD_PADDING: int = 12


class BoardWidget(AnchorLayout):
    """Self-contained board display widget.

    Owns the cell grid, border styling, and line-clear animations.
    Knows nothing about the model — callers pass grid/piece data explicitly.
    """

    def __init__(
        self,
        renderer: BlockRenderer,
        rows: int,
        cols: int,
        cell_size: float,
        padding: int,
        **kwargs: Any,
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._padding = padding
        self._renderer = renderer
        self._animating = False

        board_w = cols * cell_size + (cols - 1)
        board_h = rows * cell_size + (rows - 1)
        container_w = board_w + 2 * padding
        container_h = board_h + 2 * padding

        super().__init__(
            size_hint=(None, None),
            size=(container_w, container_h),
            **kwargs,
        )

        self._board_widget = GridLayout(
            cols=cols,
            rows=rows,
            size_hint=(None, None),
            size=(board_w, board_h),
            spacing=1,
        )

        self._board_cells: list[list[Cell]] = []
        for _ in range(rows):
            row_cells: list[Cell] = []
            for _ in range(cols):
                cell = Cell(size_hint=(1, 1))
                self._board_widget.add_widget(cell)
                row_cells.append(cell)
            self._board_cells.append(row_cells)

        with self.canvas.before:
            Color(0.35, 0.35, 0.55, 1)
            self._board_border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, 15),
                width=2,
            )

        def _update_border(*_: Any) -> None:
            self._board_border.rounded_rectangle = (
                self.x, self.y, self.width, self.height, 15,
            )

        self.bind(pos=_update_border, size=_update_border)
        self.add_widget(self._board_widget)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_animating(self) -> bool:
        """True while line-clear animation is running.

        The setter is intentionally public: GameScreen.update() sets this True
        synchronously on the model thread when LINES_CLEARED arrives, before
        scheduling _dispatch via Clock — ensuring BOARD_UPDATED callbacks
        queued ahead of LINES_CLEARED already see the flag set.
        """
        return self._animating

    @is_animating.setter
    def is_animating(self, value: bool) -> None:
        self._animating = value

    @property
    def board_size(self) -> tuple[float, float]:
        return (self._board_widget.width, self._board_widget.height)

    @property
    def container_size(self) -> tuple[float, float]:
        return (self.width, self.height)

    def redraw(
        self,
        grid: list[list[int]],
        shadow_row: int,
        piece: Optional[ITetromino],
        cur_col: int,
    ) -> None:
        """Repaint every cell from board state + ghost shadow."""
        shadow_cells: set[tuple[int, int]] = set()
        if piece is not None:
            for r, row in enumerate(piece.shape):
                for c, val in enumerate(row):
                    if val != 0:
                        shadow_cells.add((shadow_row + r, cur_col + c))

        for r in range(self._rows):
            for c in range(self._cols):
                cell_val = grid[r][c] if r < len(grid) and c < len(grid[r]) else 0
                if cell_val != 0:
                    self._render_cell(r, c, cell_val)
                elif (r, c) in shadow_cells:
                    self._board_cells[r][c].set_colour(self._renderer.shadow_colour())
                else:
                    self._board_cells[r][c].set_colour(BLOCK_COLOURS[0])

    def animate_line_clear(
        self,
        rows: list[int],
        snapshot: list[list[int]],
        on_done: Optional[Callable[[], None]] = None,
    ) -> None:
        """Flash cleared rows white one-by-one, then animate remaining rows dropping.

        Sets is_animating=True on entry and False after drop completes.
        Calls on_done() when fully finished.
        """
        self._animating = True
        self._animate_flash(rows, snapshot, 0, on_done)

    def resize(self, cell_size: float) -> None:
        """Resize board grid and container for a new cell_size."""
        board_w = self._cols * cell_size + (self._cols - 1)
        board_h = self._rows * cell_size + (self._rows - 1)
        self._board_widget.size = (board_w, board_h)
        self.size = (board_w + 2 * self._padding, board_h + 2 * self._padding)

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------

    def _render_cell(self, row: int, col: int, val: int) -> None:
        tex = self._renderer.texture(val) if val != 0 else None
        if tex is not None:
            self._board_cells[row][col].set_texture(tex)
        else:
            self._board_cells[row][col].set_colour(self._renderer.colour(val))

    def _animate_flash(
        self,
        rows: list[int],
        snapshot: list[list[int]],
        idx: int,
        on_done: Optional[Callable[[], None]],
    ) -> None:
        if idx < len(rows):
            for c in range(self._cols):
                self._board_cells[rows[idx]][c].set_colour((1.0, 1.0, 1.0, 1.0))
            Clock.schedule_once(
                lambda _dt, i=idx: self._animate_flash(rows, snapshot, i + 1, on_done),
                0.1,
            )
        else:
            self._animate_drop(rows, snapshot, 0, on_done)

    def _animate_drop(
        self,
        rows: list[int],
        snapshot: list[list[int]],
        step: int,
        on_done: Optional[Callable[[], None]],
    ) -> None:
        cleared_set: set[int] = set(rows)
        empty = BLOCK_COLOURS[0]

        for r in range(self._rows):
            for c in range(self._cols):
                self._board_cells[r][c].set_colour(empty)

        for r in range(self._rows):
            if r in cleared_set:
                continue
            drop_amount = sum(1 for cr in rows if cr > r)
            current_pos = r + min(step, drop_amount)
            if 0 <= current_pos < self._rows:
                for c in range(self._cols):
                    val = snapshot[r][c]
                    if val != 0:
                        self._render_cell(current_pos, c, val)

        if step < len(rows):
            Clock.schedule_once(
                lambda *_: self._animate_drop(rows, snapshot, step + 1, on_done),
                0.1,
            )
        else:
            self._animating = False
            if on_done is not None:
                on_done()
