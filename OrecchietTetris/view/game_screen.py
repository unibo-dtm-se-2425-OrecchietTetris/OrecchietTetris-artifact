from __future__ import annotations

from typing import Any, Callable, Optional

from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.gridlayout import GridLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.button import Button  # type: ignore[import-untyped]
from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]
from kivy.clock import Clock  # type: ignore[import-untyped]
from kivy.core.window import Window  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.model.interfaces import ITetris
from OrecchietTetris.view.interfaces import IView
import i18n  # type: ignore[import-untyped]
from OrecchietTetris.view.block_renderer import BlockRenderer, BLOCK_COLOURS


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BOARD_ROWS = 20
BOARD_COLS = 10
CELL_SIZE = 30          # pixels
PANEL_WIDTH = 160       # right-side info panel


# ---------------------------------------------------------------------------
# Helper: tiny coloured rectangle widget used for individual board cells
# ---------------------------------------------------------------------------

class _Cell(Widget):
    """A single board cell drawn via canvas instructions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        with self.canvas:
            self._color_instr = Color(0.1, 0.1, 0.1, 1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._redraw, size=self._redraw)

    def set_colour(self, rgba: tuple[float, float, float, float]) -> None:
        self._color_instr.rgba = rgba
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _redraw(self, *_: Any) -> None:
        self._rect.pos = self.pos
        self._rect.size = self.size


# ---------------------------------------------------------------------------
# Small piece-preview widget (hold / next)
# ---------------------------------------------------------------------------

class _PiecePreview(Widget):
    """Renders a 4×4 preview of a tetromino shape."""

    PREVIEW_COLS = 4
    PREVIEW_ROWS = 4
    CELL = 20

    def __init__(self, renderer: BlockRenderer, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._renderer = renderer
        self._cells: list[list[_Cell]] = []
        self._build()

    def _build(self) -> None:
        for r in range(self.PREVIEW_ROWS):
            row_cells: list[_Cell] = []
            for c in range(self.PREVIEW_COLS):
                cell = _Cell(
                    size=(self.CELL, self.CELL),
                    size_hint=(None, None),
                    pos=(self.x + c * self.CELL, self.y + (self.PREVIEW_ROWS - 1 - r) * self.CELL),
                )
                self.add_widget(cell)
                row_cells.append(cell)
            self._cells.append(row_cells)
        self.bind(pos=self._reposition)

    def _reposition(self, *_: Any) -> None:
        for r, row_cells in enumerate(self._cells):
            for c, cell in enumerate(row_cells):
                cell.pos = (
                    self.x + c * self.CELL,
                    self.y + (self.PREVIEW_ROWS - 1 - r) * self.CELL,
                )

    def set_piece(self, shape: Optional[list[list[Any]]], greyed: bool = False) -> None:
        """Render *shape* centred in the preview grid.  *shape=None* clears."""
        # Clear all cells
        for row_cells in self._cells:
            for cell in row_cells:
                cell.set_colour(BLOCK_COLOURS[0])

        if shape is None:
            return

        # Centre the shape
        row_offset = (self.PREVIEW_ROWS - len(shape)) // 2
        col_offset = (self.PREVIEW_COLS - len(shape[0])) // 2
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                pr = row_offset + r
                pc = col_offset + c
                if 0 <= pr < self.PREVIEW_ROWS and 0 <= pc < self.PREVIEW_COLS and val != 0:
                    rgba = self._renderer.colour(val)
                    if greyed:
                        rgba = (rgba[0] * 0.4, rgba[1] * 0.4, rgba[2] * 0.4, 0.6)
                    self._cells[pr][pc].set_colour(rgba)


# ---------------------------------------------------------------------------
# GameScreen
# ---------------------------------------------------------------------------

class GameScreen(Screen, IView):
    """Main game screen.

    Responsibilities
    ----------------
    * Render the 10×20 board, the falling piece, and the ghost (shadow).
    * Show next-piece and held-piece previews.
    * Display score / level / lines labels.
    * React to all ``EventType`` events from the model.
    * Handle keyboard input and forward it to the model.
    * Show a game-over overlay when the game ends.

    Parameters
    ----------
    model:
        The ``ITetris`` implementation.  The screen attaches itself as an
        observer after being shown.
    on_back_to_menu:
        Callback invoked when the player chooses to return to the menu.
    """

    def __init__(
        self,
        model: ITetris,
        on_back_to_menu: Optional[Callable[[], None]] = None,
        on_try_again: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._model = model
        self._on_back_to_menu = on_back_to_menu
        self._on_try_again = on_try_again
        self._renderer = BlockRenderer()
        self._keyboard: Any = None
        self._overlay: Optional[Widget] = None
        self._quit_overlay: Optional[Widget] = None

        self._board_cells: list[list[_Cell]] = []
        self._clearing_animation: bool = False
        self._build_ui()

    # ------------------------------------------------------------------
    # IView
    # ------------------------------------------------------------------

    def show(self) -> None:
        self.opacity = 1.0
        self.disabled = False
        self._model.attach(self)
        self._bind_keyboard()

    def hide(self) -> None:
        self.opacity = 0.0
        self.disabled = True
        self._model.detach(self)
        self._unbind_keyboard()

    # ------------------------------------------------------------------
    # Observer
    # ------------------------------------------------------------------

    def update(self, event_type: EventType, data: Any) -> None:
        # Kivy UI must be updated from the main thread.
        # For LINES_CLEARED we set the animation flag immediately (before any
        # scheduled callbacks run) so the BOARD_UPDATED that is queued ahead of
        # it does not overwrite the cells with the already-final model state.
        if event_type == EventType.LINES_CLEARED:
            self._clearing_animation = True
        Clock.schedule_once(lambda dt: self._dispatch(event_type, data))

    def _dispatch(self, event_type: EventType, data: Any) -> None:
        if event_type == EventType.BOARD_UPDATED:
            if not self._clearing_animation:
                self._redraw_board()
        elif event_type == EventType.NEW_PIECE:
            self._update_next_preview()
            if not self._clearing_animation:
                self._redraw_board()
        elif event_type == EventType.LINES_CLEARED:
            self._lbl_lines.text = f"{i18n.t('lines')}: {self._model.lines_cleared}"
            cleared_rows, pre_clear_grid = data
            rows: list[int] = list(cleared_rows)
            snapshot: list[list[tuple[float, float, float, float]]] = [
                [self._renderer.colour(pre_clear_grid[r][c]) for c in range(BOARD_COLS)]
                for r in range(BOARD_ROWS)
            ]
            self._animate_line_clear(rows, snapshot, 0)
        elif event_type == EventType.SCORE_UPDATED:
            self._lbl_score.text = f"{i18n.t('score')}: {self._model.score}"
            self._lbl_level.text = f"{i18n.t('level')}: {self._model.level}"
        elif event_type == EventType.GAME_OVER:
            self._show_game_over_overlay()
        elif event_type == EventType.PAUSED:
            self._btn_pause.text = i18n.t("resume")
        elif event_type == EventType.RESUMED:
            self._btn_pause.text = i18n.t("pause")
        elif event_type == EventType.HOLD_UPDATED:
            self._update_hold_preview()

    # ------------------------------------------------------------------
    # Board rendering
    # ------------------------------------------------------------------

    def _redraw_board(self) -> None:
        """Repaint every cell from the model's grid + shadow."""
        grid = self._model.board.grid
        shadow_row = self._model.shadow_row
        piece = self._model.current_piece
        cur_col = self._model.current_col

        # Build a shadow overlay
        shadow_cells: set[tuple[int, int]] = set()
        if piece is not None:
            for r, row in enumerate(piece.shape):
                for c, val in enumerate(row):
                    if val != 0:
                        shadow_cells.add((shadow_row + r, cur_col + c))

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                cell_val = grid[r][c] if r < len(grid) and c < len(grid[r]) else 0
                if cell_val != 0:
                    colour = self._renderer.colour(cell_val)
                elif (r, c) in shadow_cells:
                    colour = self._renderer.shadow_colour()
                else:
                    colour = BLOCK_COLOURS[0]
                self._board_cells[r][c].set_colour(colour)

    def _animate_line_clear(
        self,
        rows: list[int],
        snapshot: list[list[tuple[float, float, float, float]]],
        idx: int,
    ) -> None:
        """Flash cleared rows white one by one (bottom to top), then start drop animation."""
        if idx < len(rows):
            for c in range(BOARD_COLS):
                self._board_cells[rows[idx]][c].set_colour((1.0, 1.0, 1.0, 1.0))
            Clock.schedule_once(
                lambda _dt, i=idx: self._animate_line_clear(rows, snapshot, i + 1), 0.1
            )
        else:
            self._animate_drop(rows, snapshot, 0)

    def _animate_drop(
        self,
        rows: list[int],
        snapshot: list[list[tuple[float, float, float, float]]],
        step: int,
    ) -> None:
        """Animate remaining rows falling to their final positions after line clear.

        *rows* are the cleared row indices (sorted descending, bottom first).
        At each step every non-cleared row moves down by one position until it
        reaches its final resting place; then ``_redraw_board`` syncs with the model.
        """
        cleared_set: set[int] = set(rows)
        empty = BLOCK_COLOURS[0]

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                self._board_cells[r][c].set_colour(empty)

        for r in range(BOARD_ROWS):
            if r in cleared_set:
                continue
            drop_amount = sum(1 for cr in rows if cr > r)
            current_pos = r + min(step, drop_amount)
            if 0 <= current_pos < BOARD_ROWS:
                for c in range(BOARD_COLS):
                    self._board_cells[current_pos][c].set_colour(snapshot[r][c])

        if step < len(rows):
            Clock.schedule_once(
                lambda *_: self._animate_drop(rows, snapshot, step + 1), 0.1
            )
        else:
            self._clearing_animation = False
            self._redraw_board()

    def _update_next_preview(self) -> None:
        nxt = self._model.next_piece
        self._next_preview.set_piece(nxt.shape if nxt else None)

    def _update_hold_preview(self) -> None:
        held = self._model.held_piece
        can = self._model.can_hold
        self._hold_preview.set_piece(held.shape if held else None, greyed=not can)

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def _bind_keyboard(self) -> None:
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

    def _unbind_keyboard(self) -> None:
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.release()
            self._keyboard = None

    def _on_keyboard_closed(self) -> None:
        self._keyboard = None

    def _on_key_down(self, _keyboard: Any, keycode: tuple[int, str], _text: str,
                     _modifiers: Any) -> bool:
        _, key = keycode
        if self._model.is_game_over:
            return False
        if key == "left":
            self._model.move_left()
        elif key == "right":
            self._model.move_right()
        elif key == "down":
            self._model.move_down()
        elif key in ("up", "x"):
            self._model.rotate()
        elif key == "spacebar":
            self._model.hard_drop()
        elif key == "c":
            self._model.hold()
        elif key in ("p", "escape"):
            if self._model.is_paused:
                self._model.resume()
            else:
                self._model.pause()
        return True

    # ------------------------------------------------------------------
    # Game-over overlay
    # ------------------------------------------------------------------

    def _show_game_over_overlay(self) -> None:
        if self._overlay is not None:
            return
        overlay = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15,
            size=self.size,
            pos=self.pos,
            size_hint=(None, None),
        )
        with overlay.canvas.before:
            Color(0, 0, 0, 0.75)
            Rectangle(pos=overlay.pos, size=overlay.size)

        overlay.add_widget(Label(
            text=i18n.t("game_over"),
            font_size="40sp",
            bold=True,
            color=(0.9, 0.2, 0.2, 1),
        ))
        overlay.add_widget(Label(
            text=f"{i18n.t('score')}: {self._model.score}",
            font_size="26sp",
            color=(1, 1, 1, 1),
        ))
        btn_try = Button(
            text=i18n.t("try_again"),
            font_size="22sp",
            size_hint=(0.6, None),
            height=50,
            pos_hint={"center_x": 0.5},
            background_color=(0.2, 0.7, 0.2, 1),
        )
        btn_try.bind(on_release=self._handle_try_again)
        overlay.add_widget(btn_try)

        btn = Button(
            text=i18n.t("back_to_menu"),
            font_size="22sp",
            size_hint=(0.6, None),
            height=50,
            pos_hint={"center_x": 0.5},
            background_color=(0.9, 0.5, 0.1, 1),
        )
        btn.bind(on_release=self._handle_back_to_menu)
        overlay.add_widget(btn)
        self.add_widget(overlay)
        self._overlay = overlay

    def _handle_back_to_menu(self, *_: Any) -> None:
        if self._overlay is not None:
            self.remove_widget(self._overlay)
            self._overlay = None
        if self._on_back_to_menu is not None:
            self._on_back_to_menu()

    def _handle_try_again(self, *_: Any) -> None:
        if self._overlay is not None:
            self.remove_widget(self._overlay)
            self._overlay = None
        if self._on_try_again is not None:
            self._on_try_again()
    # ------------------------------------------------------------------
    # Pause button callback
    # ------------------------------------------------------------------

    def _handle_pause(self, *_: Any) -> None:
        if self._model.is_paused:
            self._model.resume()
        else:
            self._model.pause()

    def _handle_quit(self, *_: Any) -> None:
        if self._model.is_running and not self._model.is_paused:
            self._model.pause()
        self._show_quit_confirm_overlay()

    def _show_quit_confirm_overlay(self) -> None:
        if self._quit_overlay is not None:
            return
        overlay = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15,
            size=self.size,
            pos=self.pos,
            size_hint=(None, None),
        )
        with overlay.canvas.before:
            Color(0, 0, 0, 0.75)
            Rectangle(pos=overlay.pos, size=overlay.size)

        overlay.add_widget(Label(
            text=i18n.t("quit_confirm"),
            font_size="32sp",
            bold=True,
            color=(1, 1, 1, 1),
        ))

        btn_row = BoxLayout(orientation="horizontal", size_hint=(0.6, None),
                            height=50, pos_hint={"center_x": 0.5}, spacing=10)
        btn_yes = Button(text=i18n.t("yes"), font_size="22sp",
                         background_color=(0.7, 0.15, 0.15, 1))
        btn_no = Button(text=i18n.t("no"), font_size="22sp",
                        background_color=(0.3, 0.3, 0.7, 1))
        btn_yes.bind(on_release=self._confirm_quit)
        btn_no.bind(on_release=self._dismiss_quit_overlay)
        btn_row.add_widget(btn_yes)
        btn_row.add_widget(btn_no)
        overlay.add_widget(btn_row)

        self.add_widget(overlay)
        self._quit_overlay = overlay

    def _dismiss_quit_overlay(self, *_: Any) -> None:
        if self._quit_overlay is not None:
            self.remove_widget(self._quit_overlay)
            self._quit_overlay = None
        if self._model.is_paused:
            self._model.resume()

    def _confirm_quit(self, *_: Any) -> None:
        if self._quit_overlay is not None:
            self.remove_widget(self._quit_overlay)
            self._quit_overlay = None
        if self._model.is_running:
            self._model.stop()
        if self._on_back_to_menu is not None:
            self._on_back_to_menu()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        with self.canvas.before:
            Color(0.05, 0.05, 0.10, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = BoxLayout(orientation="horizontal", spacing=10, padding=10)

        # ---- Board ----
        board_widget = GridLayout(
            cols=BOARD_COLS,
            rows=BOARD_ROWS,
            size_hint=(None, None),
            size=(BOARD_COLS * CELL_SIZE, BOARD_ROWS * CELL_SIZE),
            row_force_default=True,
            row_default_height=CELL_SIZE,
            col_force_default=True,
            col_default_width=CELL_SIZE,
            spacing=1,
        )

        for r in range(BOARD_ROWS):
            row_cells: list[_Cell] = []
            for c in range(BOARD_COLS):
                cell = _Cell(
                    size=(CELL_SIZE, CELL_SIZE),
                    size_hint=(None, None),
                )
                board_widget.add_widget(cell)
                row_cells.append(cell)
            self._board_cells.append(row_cells)

        root.add_widget(board_widget)

        # ---- Right panel ----
        panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, 1),
            width=PANEL_WIDTH,
            spacing=12,
            padding=8,
        )

        # Score / level / lines
        self._lbl_score = Label(
            text=f"{i18n.t('score')}: 0",
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=30,
        )
        self._lbl_level = Label(
            text=f"{i18n.t('level')}: 1",
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=30,
        )
        self._lbl_lines = Label(
            text=f"{i18n.t('lines')}: 0",
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=30,
        )

        for lbl in (self._lbl_score, self._lbl_level, self._lbl_lines):
            panel.add_widget(lbl)

        # Next piece
        panel.add_widget(Label(
            text=i18n.t("next"),
            font_size="14sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, None),
            height=22,
        ))
        self._next_preview = _PiecePreview(
            self._renderer,
            size=(_PiecePreview.CELL * _PiecePreview.PREVIEW_COLS,
                  _PiecePreview.CELL * _PiecePreview.PREVIEW_ROWS),
            size_hint=(None, None),
        )
        panel.add_widget(self._next_preview)

        # Hold piece
        panel.add_widget(Label(
            text=i18n.t("hold"),
            font_size="14sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, None),
            height=22,
        ))
        self._hold_preview = _PiecePreview(
            self._renderer,
            size=(_PiecePreview.CELL * _PiecePreview.PREVIEW_COLS,
                  _PiecePreview.CELL * _PiecePreview.PREVIEW_ROWS),
            size_hint=(None, None),
        )
        panel.add_widget(self._hold_preview)

        # Pause button
        self._btn_pause = Button(
            text=i18n.t("pause"),
            font_size="16sp",
            size_hint=(1, None),
            height=40,
            background_color=(0.3, 0.3, 0.7, 1),
        )
        self._btn_pause.bind(on_release=self._handle_pause)
        panel.add_widget(self._btn_pause)

        # Quit button
        self._btn_quit = Button(
            text=i18n.t("quit"),
            font_size="16sp",
            size_hint=(1, None),
            height=40,
            background_color=(0.7, 0.15, 0.15, 1),
        )
        self._btn_quit.bind(on_release=self._handle_quit)
        panel.add_widget(self._btn_quit)

        panel.add_widget(Widget())  # spacer
        root.add_widget(panel)

        self.add_widget(root)

    def _update_bg(self, *_: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
