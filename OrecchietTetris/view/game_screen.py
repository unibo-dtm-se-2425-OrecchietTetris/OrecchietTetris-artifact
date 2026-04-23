from __future__ import annotations

import os
from typing import Any, Callable, Optional

from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore[import-untyped]
from kivy.uix.gridlayout import GridLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle  # type: ignore[import-untyped]
from kivy.clock import Clock  # type: ignore[import-untyped]
from kivy.core.window import Window  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.model.interfaces import ITetris
from OrecchietTetris.view.interfaces import IView
import i18n  # type: ignore[import-untyped]
from OrecchietTetris.view.block_renderer import BlockRenderer, BLOCK_COLOURS
from OrecchietTetris.view.widgets import Cell, PiecePreview, TitledBox, RoundedButton, DialogOverlay


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
GAME_SCREEN_BG: str = os.path.join(_ASSETS_DIR, "game_screen.webp")

BOARD_ROWS = 20
BOARD_COLS = 10
CELL_SIZE = 30          # pixels
PANEL_WIDTH = 160       # right-side info panel
BOARD_PADDING = 12      # padding + border around the board


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cover_tex_coords(
    img_w: float, img_h: float, win_w: float, win_h: float
) -> tuple[float, ...]:
    """Compute Kivy tex_coords for CSS-style cover: fill window, center, crop to fit."""
    if img_h == 0 or win_h == 0:
        return (0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)
    img_ratio = img_w / img_h
    win_ratio = win_w / win_h
    if img_ratio > win_ratio:
        shown_w = win_ratio / img_ratio
        u0 = (1.0 - shown_w) / 2.0
        return (u0, 1.0, u0 + shown_w, 1.0, u0 + shown_w, 0.0, u0, 0.0)
    shown_h = img_ratio / win_ratio
    v0 = (1.0 - shown_h) / 2.0
    v1 = v0 + shown_h
    return (0.0, v1, 1.0, v1, 1.0, v0, 0.0, v0)


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
        self._pause_overlay: Optional[Widget] = None

        self._board_cells: list[list[Cell]] = []
        self._clearing_animation: bool = False
        self._countdown_overlay: Optional[Widget] = None
        self._on_try_again = self.start_with_countdown
        self._root: BoxLayout
        self._board_container: AnchorLayout
        self._board_widget: GridLayout
        self._hold_box: TitledBox
        self._next_box: TitledBox
        self._title_score: Label
        self._title_level: Label
        self._title_lines: Label
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
            self._lbl_lines.text = str(self._model.lines_cleared)
            cleared_rows, pre_clear_grid = data
            rows: list[int] = list(cleared_rows)
            snapshot: list[list[int]] = [
                [pre_clear_grid[r][c] for c in range(BOARD_COLS)]
                for r in range(BOARD_ROWS)
            ]
            self._animate_line_clear(rows, snapshot, 0)
        elif event_type == EventType.SCORE_UPDATED:
            self._lbl_score.text = str(self._model.score)
            self._lbl_level.text = str(self._model.level)
        elif event_type == EventType.GAME_OVER:
            self._show_game_over_overlay()
        elif event_type == EventType.PAUSED:
            self._btn_pause.text = ""
            self._show_pause_overlay()
        elif event_type == EventType.RESUMED:
            self._btn_pause.text = ""
            self._dismiss_pause_overlay()
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
        dlg = DialogOverlay(
            title=i18n.t("game_over"),
            title_color=(0.9, 0.2, 0.2, 1),
        )
        dlg.add_label(
            f"{i18n.t('score')}: {self._model.score}",
            font_size="24sp",
        )
        dlg.add_button(
            text="",
            bg=(0.3, 0.3, 0.7, 1),
            on_release=self._handle_try_again,
            font_name="MaterialIcons",
            font_size="28sp",
        )
        dlg.add_button(
            text="",
            bg=(0.7, 0.15, 0.15, 1),
            on_release=self._handle_back_to_menu,
            font_name="MaterialIcons",
            font_size="28sp",
        )
        self.add_widget(dlg)
        self._overlay = dlg

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
    # Pause overlay
    # ------------------------------------------------------------------

    def _handle_pause(self, *_: Any) -> None:
        if self._model.is_paused:
            self._dismiss_pause_overlay()
            self._show_countdown(self._model.resume)
        else:
            self._model.pause()

    def _show_pause_overlay(self) -> None:
        if self._pause_overlay is not None or self._quit_overlay is not None:
            return
        dlg = DialogOverlay(title=i18n.t("paused"))
        dlg.add_button(
            text="",
            bg=(0.3, 0.3, 0.7, 1),
            on_release=self._handle_pause,
            font_name="MaterialIcons",
            font_size="28sp",
        )
        dlg.add_button(
            text="",
            bg=(0.7, 0.15, 0.15, 1),
            on_release=self._handle_quit,
            font_name="MaterialIcons",
            font_size="28sp",
        )
        self.add_widget(dlg)
        self._pause_overlay = dlg

    def _dismiss_pause_overlay(self, *_: Any) -> None:
        if self._pause_overlay is not None:
            self.remove_widget(self._pause_overlay)
            self._pause_overlay = None

    # ------------------------------------------------------------------
    # Quit overlay
    # ------------------------------------------------------------------

    def _handle_quit(self, *_: Any) -> None:
        if self._quit_overlay is not None:
            return
        if self._model.is_running and not self._model.is_paused:
            self._model.pause()
        self._show_quit_confirm_overlay()

    def _show_quit_confirm_overlay(self) -> None:
        if self._quit_overlay is not None:
            return
        dlg = DialogOverlay(title=i18n.t("quit_confirm"))
        dlg.add_button_row([
            {"text": i18n.t("no"),  "bg": (0.3, 0.3, 0.7, 1),  "on_release": self._dismiss_quit_overlay},
            {"text": i18n.t("yes"), "bg": (0.7, 0.15, 0.15, 1), "on_release": self._confirm_quit},
        ])
        self.add_widget(dlg)
        self._quit_overlay = dlg

    def _dismiss_quit_overlay(self, *_: Any) -> None:
        if self._quit_overlay is not None:
            self.remove_widget(self._quit_overlay)
            self._quit_overlay = None
        if self._pause_overlay is None and self._model.is_paused:
            self._model.resume()

    def _confirm_quit(self, *_: Any) -> None:
        if self._quit_overlay is not None:
            self.remove_widget(self._quit_overlay)
            self._quit_overlay = None
        self._dismiss_pause_overlay()
        if self._model.is_running:
            self._model.stop()
        if self._on_back_to_menu is not None:
            self._on_back_to_menu()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _load_bg_image(self) -> None:
        """Load game_screen.webp as background texture (requires live Kivy context)."""
        if not os.path.exists(GAME_SCREEN_BG):
            return
        from kivy.core.image import Image as CoreImage  # type: ignore[import-untyped]
        self._bg_core_image = CoreImage(GAME_SCREEN_BG)
        self._bg_image_color.a = 1
        self._bg_rect.texture = self._bg_core_image.texture
        self._update_bg()

    def _build_ui(self) -> None:
        self._bg_core_image = None
        with self.canvas.before:
            Color(0.05, 0.05, 0.10, 1)
            self._bg_fill_rect = Rectangle(pos=self.pos, size=self.size)
            self._bg_image_color = Color(1, 1, 1, 0)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0, 0, 0, 0.45)
            self._bg_overlay_rect = Rectangle(pos=self.pos, size=self.size)
        self._load_bg_image()
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

        preview_px = PANEL_WIDTH - 2 * TitledBox._PAD
        box_h = preview_px + TitledBox._TITLE_H + 2 * TitledBox._PAD

        # Hold box
        self._hold_box = TitledBox(
            title=i18n.t("hold"),
            size_hint=(1, None),
            height=box_h,
        )
        self._hold_preview = PiecePreview(
            self._renderer,
            size=(preview_px, preview_px),
            size_hint=(None, None),
        )
        self._hold_box.set_content(self._hold_preview)
        left_panel.add_widget(self._hold_box)

        left_panel.add_widget(Widget())  # flexible spacer

        # Stats box
        title_h = TitledBox._TITLE_H
        val_h = 40
        stats_inner_h = 3 * (title_h + val_h)
        stats_inner_w = PANEL_WIDTH - 2 * TitledBox._PAD
        stats_inner = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(stats_inner_w, stats_inner_h),
            spacing=4,
        )

        def _make_stats_title(text: str) -> Label:
            return Label(
                text=text,
                font_size="13sp",
                bold=True,
                color=(0.70, 0.70, 0.90, 1),
                size_hint=(1, None),
                height=title_h,
            )

        def _make_stat_value_box(initial: str) -> tuple[BoxLayout, Label]:
            box = BoxLayout(size_hint=(1, None), height=val_h)
            with box.canvas.before:
                Color(*BLOCK_COLOURS[0])
                bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[12])
            box.bind(
                pos=lambda w, _: setattr(bg, 'pos', w.pos),
                size=lambda w, _: setattr(bg, 'size', w.size),
            )
            lbl = Label(
                text=initial,
                font_size="22sp",
                bold=True,
                color=(1, 1, 1, 1),
                size_hint=(1, 1),
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lambda inst, s: setattr(inst, 'text_size', s))
            box.add_widget(lbl)
            return box, lbl

        self._title_score = _make_stats_title(i18n.t('score'))
        _box_score, self._lbl_score = _make_stat_value_box("0")
        self._title_level = _make_stats_title(i18n.t('level'))
        _box_level, self._lbl_level = _make_stat_value_box("1")
        self._title_lines = _make_stats_title(i18n.t('lines'))
        _box_lines, self._lbl_lines = _make_stat_value_box("0")
        for w in (
            self._title_score, _box_score,
            self._title_level, _box_level,
            self._title_lines, _box_lines,
        ):
            stats_inner.add_widget(w)

        stats_box_h = stats_inner_h + TitledBox._TITLE_H + 2 * TitledBox._PAD
        stats_box = TitledBox(
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
            row_cells: list[Cell] = []
            for c in range(BOARD_COLS):
                cell = Cell(size_hint=(1, 1))
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
                rounded_rectangle=(
                    board_container.x, board_container.y,
                    board_container.width, board_container.height,
                    20,
                ),
                width=2,
            )

        def _update_border(*_: Any) -> None:
            self._board_border.rounded_rectangle = (
                board_container.x, board_container.y,
                board_container.width, board_container.height,
                15,
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
        self._next_box = TitledBox(
            title=i18n.t("next"),
            size_hint=(1, None),
            height=box_h,
        )
        self._next_preview = PiecePreview(
            self._renderer,
            size=(preview_px, preview_px),
            size_hint=(None, None),
        )
        self._next_box.set_content(self._next_preview)
        right_panel.add_widget(self._next_box)

        right_panel.add_widget(Widget())  # flexible spacer

        # Pause button
        self._btn_pause = RoundedButton(
            text="",
            font_name="MaterialIcons",
            font_size="30sp",
            size_hint=(1, None),
            height=60,
            background_color=(0.3, 0.3, 0.7, 1),
        )
        self._btn_pause.bind(on_release=self._handle_pause)
        right_panel.add_widget(self._btn_pause)

        # Quit button
        self._btn_quit = RoundedButton(
            text="",
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
        self._title_score.text = i18n.t('score')
        self._title_level.text = i18n.t('level')
        self._title_lines.text = i18n.t('lines')
        self._hold_box.set_title(i18n.t("hold"))
        self._next_box.set_title(i18n.t("next"))
        self._btn_pause.text = "" if self._model.is_paused else ""

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
        self._update_bg()

    def _update_bg(self, *_: Any) -> None:
        self._bg_fill_rect.pos = self.pos
        self._bg_fill_rect.size = self.size
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_overlay_rect.pos = self.pos
        self._bg_overlay_rect.size = self.size
        if self._bg_core_image is not None:
            tex = self._bg_core_image.texture
            self._bg_rect.tex_coords = _cover_tex_coords(
                tex.width, tex.height, self.width, self.height
            )
