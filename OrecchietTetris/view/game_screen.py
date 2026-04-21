from __future__ import annotations

from typing import Any, Callable, Optional

from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore[import-untyped]
from kivy.uix.gridlayout import GridLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.button import Button  # type: ignore[import-untyped]
from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle, Line  # type: ignore[import-untyped]
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
BOARD_PADDING = 10      # padding + border around the board


# ---------------------------------------------------------------------------
# Helper: tiny coloured rectangle widget used for individual board cells
# ---------------------------------------------------------------------------

class _Cell(Widget):
    """A single board cell drawn via canvas instructions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        with self.canvas:
            # Layer 1: solid background (always the empty-cell colour for filled
            # cells so transparent image pixels match empty neighbours).
            self._color_instr = Color(*BLOCK_COLOURS[0])
            self._rect = Rectangle(pos=self.pos, size=self.size)
            # Layer 2: image drawn on top; hidden until set_texture is called.
            self._img_color = Color(1.0, 1.0, 1.0, 0.0)
            self._img_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._redraw, size=self._redraw)

    def set_colour(self, rgba: tuple[float, float, float, float]) -> None:
        self._color_instr.rgba = rgba
        self._rect.texture = None
        self._img_color.a = 0.0

    def set_texture(self, texture: object, alpha: float = 1.0) -> None:
        self._color_instr.rgba = BLOCK_COLOURS[0]
        self._rect.texture = None
        self._img_color.rgba = (1.0, 1.0, 1.0, alpha)
        self._img_rect.texture = texture
        self._img_rect.pos = self.pos
        self._img_rect.size = self.size

    def _redraw(self, *_: Any) -> None:
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._img_rect.pos = self.pos
        self._img_rect.size = self.size


# ---------------------------------------------------------------------------
# Small piece-preview widget (hold / next)
# ---------------------------------------------------------------------------

class _PiecePreview(Widget):
    """Renders a 4×4 preview of a tetromino shape."""

    PREVIEW_COLS = 6
    PREVIEW_ROWS = 6
    CELL = PREVIEW_ROWS * PREVIEW_COLS

    def __init__(self, renderer: BlockRenderer, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._renderer = renderer
        self._cells: list[list[_Cell]] = []
        self._build()

    def _build(self) -> None:
        for _ in range(self.PREVIEW_ROWS):
            row_cells: list[_Cell] = []
            for _ in range(self.PREVIEW_COLS):
                cell = _Cell(size_hint=(None, None))
                self.add_widget(cell)
                row_cells.append(cell)
            self._cells.append(row_cells)
        self.bind(pos=self._reposition, size=self._reposition)

    def _reposition(self, *_: Any) -> None:
        cs = min(self.width / self.PREVIEW_COLS, self.height / self.PREVIEW_ROWS)
        for r, row_cells in enumerate(self._cells):
            for c, cell in enumerate(row_cells):
                cell.size = (cs, cs)
                cell.pos = (
                    self.x + c * cs,
                    self.y + (self.PREVIEW_ROWS - 1 - r) * cs,
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
                    tex = self._renderer.texture(val)
                    if tex is not None:
                        self._cells[pr][pc].set_texture(tex, alpha=0.35 if greyed else 1.0)
                    else:
                        rgba = self._renderer.colour(val)
                        if greyed:
                            rgba = (rgba[0] * 0.4, rgba[1] * 0.4, rgba[2] * 0.4, 0.6)
                        self._cells[pr][pc].set_colour(rgba)


# ---------------------------------------------------------------------------
# Titled box widget (bordered panel with overlapping title label)
# ---------------------------------------------------------------------------

class _TitledBox(Widget):
    """A bordered panel whose title label straddles the top edge.

    Layout
    ------
    The border rectangle starts at ``_TITLE_H // 2`` pixels below the widget's
    top, so the title ``Label`` — drawn at the very top — visually overlaps it,
    producing the classic "fieldset / legend" look.  A filled rectangle behind
    the label erases the border segment it covers.

    The single content widget (added via :meth:`set_content`) is centred inside
    the available area below the title.
    """

    _TITLE_H: int = 22
    _PAD: int = 8

    def __init__(self, title: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._title_str = title
        self._content_widget: Optional[Widget] = None

        with self.canvas:
            Color(0.35, 0.35, 0.55, 1)
            self._border_instr = Line(width=1.5)
            Color(0.05, 0.05, 0.10, 1)
            self._title_bg_instr = Rectangle()

        self._lbl = Label(
            text=title,
            font_size="13sp",
            bold=True,
            color=(0.70, 0.70, 0.90, 1),
            size_hint=(None, None),
            size=(80, self._TITLE_H),
        )
        self.add_widget(self._lbl)
        self.bind(pos=self._layout, size=self._layout)

    def set_title(self, text: str) -> None:
        self._title_str = text
        self._lbl.text = text
        self._layout()

    def set_content(self, widget: Widget) -> None:
        self._content_widget = widget
        self.add_widget(widget)
        self._layout()

    def _layout(self, *_: Any) -> None:
        th = self._TITLE_H
        pad = self._PAD
        x, y, w, h = self.x, self.y, self.width, self.height

        # Border occupies the bottom (h − th//2) of the widget height.
        border_h = h - th // 2
        self._border_instr.rectangle = (x + 1, y + 1, w - 2, border_h - 2)

        # Title label straddles the top edge of the border rectangle.
        lbl_w = max(60, min(w - 2 * pad, len(self._title_str) * 9 + 20))
        lbl_x = x + (w - lbl_w) / 2
        lbl_y = y + h - th
        self._lbl.size = (lbl_w, th)
        self._lbl.pos = (lbl_x, lbl_y)
        self._title_bg_instr.pos = (lbl_x, lbl_y)
        self._title_bg_instr.size = (lbl_w, th)

        # Content: fills the usable area inside the border, below the title.
        if self._content_widget is not None:
            avail_w = w - 2 * pad
            avail_h = border_h - th // 2 - 2 * pad
            self._content_widget.size = (avail_w, avail_h)
            self._content_widget.pos = (x + pad, y + pad)


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
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._model = model
        self._on_back_to_menu = on_back_to_menu
        self._renderer = BlockRenderer()
        self._renderer.preload_textures()
        self._keyboard: Any = None
        self._overlay: Optional[Widget] = None
        self._quit_overlay: Optional[Widget] = None

        self._board_cells: list[list[_Cell]] = []
        self._clearing_animation: bool = False
        self._countdown_overlay: Optional[Widget] = None
        self._on_try_again = self.start_with_countdown
        self._root: BoxLayout
        self._board_container: AnchorLayout
        self._board_widget: GridLayout
        self._hold_box: _TitledBox
        self._next_box: _TitledBox
        self._build_ui()

    # ------------------------------------------------------------------
    # IView
    # ------------------------------------------------------------------

    def show(self) -> None:
        self.opacity = 1.0
        self.disabled = False
        self._refresh_labels()
        self._model.attach(self)
        self._bind_keyboard()

    def hide(self) -> None:
        self.opacity = 0.0
        self.disabled = True
        self._model.detach(self)
        self._unbind_keyboard()

    def start_with_countdown(self) -> None:
        """Show a 3-2-1 countdown overlay then start a new game."""
        self._show_countdown(self._model.play)

    # ------------------------------------------------------------------
    # Countdown overlay
    # ------------------------------------------------------------------

    def _show_countdown(self, callback: Callable[[], None]) -> None:
        """Display 3 → 2 → 1 over the board, then invoke *callback*."""
        if self._countdown_overlay is not None:
            return
        overlay = Label(
            text="3",
            font_size="120sp",
            bold=True,
            color=(1, 1, 1, 1),
            size=self.size,
            pos=self.pos,
            size_hint=(None, None),
        )
        with overlay.canvas.before:
            Color(0, 0, 0, 0.65)
            self._countdown_bg = Rectangle(pos=overlay.pos, size=overlay.size)
        self.add_widget(overlay)
        self._countdown_overlay = overlay
        Clock.schedule_once(lambda *_: self._countdown_step(2, overlay, callback), 1.0)

    def _countdown_step(self, count: int, overlay: Any, callback: Callable[[], None]) -> None:
        if count > 0:
            overlay.text = str(count)
            Clock.schedule_once(
                lambda *_: self._countdown_step(count - 1, overlay, callback), 1.0
            )
        else:
            if self._countdown_overlay is not None:
                self.remove_widget(self._countdown_overlay)
                self._countdown_overlay = None
            callback()

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
            snapshot: list[list[int]] = [
                [pre_clear_grid[r][c] for c in range(BOARD_COLS)]
                for r in range(BOARD_ROWS)
            ]
            self._animate_line_clear(rows, snapshot, 0)
        elif event_type == EventType.SCORE_UPDATED:
            self._lbl_score.text = f"{i18n.t('score')}: {self._model.score}"
            self._lbl_level.text = f"{i18n.t('level')}: {self._model.level}"
        elif event_type == EventType.GAME_OVER:
            self._show_game_over_overlay()
        elif event_type == EventType.PAUSED:
            self._btn_pause.text = "\ue037"
        elif event_type == EventType.RESUMED:
            self._btn_pause.text = "\ue034"
        elif event_type == EventType.HOLD_UPDATED:
            self._update_hold_preview()

    # ------------------------------------------------------------------
    # Board rendering
    # ------------------------------------------------------------------

    def _render_cell(self, row: int, col: int, val: int) -> None:
        """Paint board cell at (row, col) using preloaded texture if available, else colour."""
        tex = self._renderer.texture(val) if val != 0 else None
        if tex is not None:
            self._board_cells[row][col].set_texture(tex)
        else:
            self._board_cells[row][col].set_colour(self._renderer.colour(val))

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
                    self._render_cell(r, c, cell_val)
                elif (r, c) in shadow_cells:
                    self._board_cells[r][c].set_colour(self._renderer.shadow_colour())
                else:
                    self._board_cells[r][c].set_colour(BLOCK_COLOURS[0])

    def _animate_line_clear(
        self,
        rows: list[int],
        snapshot: list[list[int]],
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
        snapshot: list[list[int]],
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
                    val = snapshot[r][c]
                    if val != 0:
                        self._render_cell(current_pos, c, val)

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
        if self._countdown_overlay is not None:
            return True
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
            self._handle_pause()
        elif key in ("q"):
            if self._quit_overlay is None:
                self._handle_quit()
            else:
                self._dismiss_quit_overlay()
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
            text="\ue042",
            font_name="MaterialIcons",
            font_size="28sp",
            size_hint=(0.6, None),
            height=50,
            pos_hint={"center_x": 0.5},
            background_color=(0.2, 0.7, 0.2, 1),
        )
        btn_try.bind(on_release=self._handle_try_again)
        overlay.add_widget(btn_try)

        btn = Button(
            text="\ue88a",
            font_name="MaterialIcons",
            font_size="28sp",
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
            self._show_countdown(self._model.resume)
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

        cell_size = self._calc_cell_size()
        board_w = BOARD_COLS * cell_size + (BOARD_COLS - 1)
        board_h = BOARD_ROWS * cell_size + (BOARD_ROWS - 1)
        total_width = board_w + 2 * BOARD_PADDING + 2 * PANEL_WIDTH + 60
        total_height = board_h + 2 * BOARD_PADDING + 20
        root = BoxLayout(
            orientation="horizontal",
            spacing=20,
            padding=10,
            size_hint=(None, None),
            width=total_width,
            height=total_height,
        )
        self._root = root

        # ----------------------------------------------------------------
        # Left column: hold box (top) + spacer + stats box (bottom)
        # ----------------------------------------------------------------
        left_panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, 1),
            width=PANEL_WIDTH,
            spacing=10,
            padding=[0, 40, 0, 40],
        )

        preview_px = PANEL_WIDTH - 2 * _TitledBox._PAD  # fill interior width → square box
        box_h = preview_px + _TitledBox._TITLE_H + 2 * _TitledBox._PAD  # 118 px

        # Hold box
        self._hold_box = _TitledBox(
            title=i18n.t("hold"),
            size_hint=(1, None),
            height=box_h,
        )
        self._hold_preview = _PiecePreview(
            self._renderer,
            size=(preview_px, preview_px),
            size_hint=(None, None),
        )
        self._hold_box.set_content(self._hold_preview)
        left_panel.add_widget(self._hold_box)

        left_panel.add_widget(Widget())  # flexible spacer

        # Stats box
        lbl_h = 30
        stats_inner_h = 3 * lbl_h
        stats_inner_w = PANEL_WIDTH - 2 * _TitledBox._PAD
        stats_inner = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(stats_inner_w, stats_inner_h),
        )
        self._lbl_score = Label(
            text=f"{i18n.t('score')}: 0",
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=lbl_h,
        )
        self._lbl_level = Label(
            text=f"{i18n.t('level')}: 1",
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=lbl_h,
        )
        self._lbl_lines = Label(
            text=f"{i18n.t('lines')}: 0",
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=lbl_h,
        )
        for lbl in (self._lbl_score, self._lbl_level, self._lbl_lines):
            stats_inner.add_widget(lbl)

        stats_box_h = stats_inner_h + _TitledBox._TITLE_H + 2 * _TitledBox._PAD
        stats_box = _TitledBox(
            title="",
            size_hint=(1, None),
            height=stats_box_h,
        )
        stats_box.set_content(stats_inner)
        left_panel.add_widget(stats_box)

        root.add_widget(left_panel)

        # ----------------------------------------------------------------
        # Centre column: the board
        # ----------------------------------------------------------------
        self._board_widget = GridLayout(
            cols=BOARD_COLS,
            rows=BOARD_ROWS,
            size_hint=(None, None),
            size=(board_w, board_h),
            spacing=1,
        )
        board_widget = self._board_widget

        for r in range(BOARD_ROWS):
            row_cells: list[_Cell] = []
            for c in range(BOARD_COLS):
                cell = _Cell(size_hint=(1, 1))
                board_widget.add_widget(cell)
                row_cells.append(cell)
            self._board_cells.append(row_cells)

        board_container = AnchorLayout(
            size_hint=(None, None),
            size=(board_w + 2 * BOARD_PADDING, board_h + 2 * BOARD_PADDING),
        )
        with board_container.canvas.before:
            Color(0.35, 0.35, 0.55, 1)
            self._board_border = Line(
                rectangle=(
                    board_container.x, board_container.y,
                    board_container.width, board_container.height
                ),
                width=2,
            )

        def _update_border(*_: Any) -> None:
            self._board_border.rectangle = (
                board_container.x, board_container.y,
                board_container.width, board_container.height,
            )

        board_container.bind(pos=_update_border, size=_update_border)
        board_container.add_widget(board_widget)
        self._board_container = board_container
        root.add_widget(board_container)

        # ----------------------------------------------------------------
        # Right column: next box (top) + spacer + pause / quit buttons
        # ----------------------------------------------------------------
        right_panel = BoxLayout(
            orientation="vertical",
            size_hint=(None, 1),
            width=PANEL_WIDTH,
            spacing=10,
            padding=[0, 40, 0, 40],
        )

        # Next box (mirrors hold box height)
        self._next_box = _TitledBox(
            title=i18n.t("next"),
            size_hint=(1, None),
            height=box_h,
        )
        self._next_preview = _PiecePreview(
            self._renderer,
            size=(preview_px, preview_px),
            size_hint=(None, None),
        )
        self._next_box.set_content(self._next_preview)
        right_panel.add_widget(self._next_box)

        right_panel.add_widget(Widget())  # flexible spacer

        # Pause button
        self._btn_pause = Button(
            text="\ue034",
            font_name="MaterialIcons",
            font_size="30sp",
            size_hint=(1, None),
            height=60,
            background_color=(0.3, 0.3, 0.7, 1),
        )
        self._btn_pause.bind(on_release=self._handle_pause)
        right_panel.add_widget(self._btn_pause)

        # Quit button
        self._btn_quit = Button(
            text="\ue9ba",
            font_name="MaterialIcons",
            font_size="30sp",
            size_hint=(1, None),
            height=60,
            background_color=(0.7, 0.15, 0.15, 1),
        )
        self._btn_quit.bind(on_release=self._handle_quit)
        right_panel.add_widget(self._btn_quit)

        root.add_widget(right_panel)

        outer = AnchorLayout(anchor_x="center", anchor_y="center")
        outer.add_widget(root)
        self.add_widget(outer)
        Window.bind(on_resize=self._on_window_resize)

    def _refresh_labels(self) -> None:
        self._lbl_score.text = f"{i18n.t('score')}: {self._model.score}"
        self._lbl_level.text = f"{i18n.t('level')}: {self._model.level}"
        self._lbl_lines.text = f"{i18n.t('lines')}: {self._model.lines_cleared}"
        self._hold_box.set_title(i18n.t("hold"))
        self._next_box.set_title(i18n.t("next"))
        self._btn_pause.text = "\ue037" if self._model.is_paused else "\ue034"

    def _calc_cell_size(self) -> float:
        win_w: float = float(Window.size[0])
        win_h: float = float(Window.size[1])
        available_h = win_h - 20 - 2 * BOARD_PADDING - (BOARD_ROWS - 1)
        available_w = win_w - 2 * PANEL_WIDTH - 60 - 2 * BOARD_PADDING - (BOARD_COLS - 1)
        return max(10.0, min(available_h / BOARD_ROWS, available_w / BOARD_COLS))

    def _on_window_resize(self, _window: Any, _w: int, _h: int) -> None:
        cell_size = self._calc_cell_size()
        board_w = BOARD_COLS * cell_size + (BOARD_COLS - 1)
        board_h = BOARD_ROWS * cell_size + (BOARD_ROWS - 1)
        self._board_widget.size = (board_w, board_h)
        self._board_container.size = (board_w + 2 * BOARD_PADDING, board_h + 2 * BOARD_PADDING)
        self._root.width = board_w + 2 * BOARD_PADDING + 2 * PANEL_WIDTH + 60
        self._root.height = board_h + 2 * BOARD_PADDING + 20

    def _update_bg(self, *_: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
