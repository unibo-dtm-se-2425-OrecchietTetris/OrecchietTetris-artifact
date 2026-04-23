# BoardWidget Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract board rendering and animation logic from `GameScreen` into a self-contained `BoardWidget(AnchorLayout)` in `view/widgets/board_widget.py`.

**Architecture:** `BoardWidget` owns all cell widgets, the border container, and animation state. `GameScreen` instantiates it, passes model data to its public methods, and checks `board.is_animating` before requesting redraws. No model reference lives inside the widget.

**Tech Stack:** Python 3, Kivy (`AnchorLayout`, `GridLayout`, `Line`, `Clock`), mypy strict, flake8 (max line 120), pytest.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `OrecchietTetris/view/widgets/board_widget.py` | **Create** | `BoardWidget` class + module-level constants |
| `OrecchietTetris/view/widgets/__init__.py` | **Modify** | Export `BoardWidget` |
| `OrecchietTetris/view/game_screen.py` | **Modify** | Use `BoardWidget`; remove extracted code |
| `tests/view/widgets/__init__.py` | **Create** | Make `tests/view/widgets/` a package |
| `tests/view/widgets/test_board_widget.py` | **Create** | Tests for exported constants |

---

## Task 1: Scaffold `board_widget.py` with constants and constructor

**Files:**
- Create: `OrecchietTetris/view/widgets/board_widget.py`
- Create: `tests/view/widgets/__init__.py`
- Create: `tests/view/widgets/test_board_widget.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/view/widgets/__init__.py` (empty):
```python
```

Create `tests/view/widgets/test_board_widget.py`:
```python
from OrecchietTetris.view.widgets.board_widget import BOARD_ROWS, BOARD_COLS, BOARD_PADDING


def test_board_constants():
    assert BOARD_ROWS == 20
    assert BOARD_COLS == 10
    assert BOARD_PADDING == 12
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
poetry run pytest tests/view/widgets/test_board_widget.py -v
```

Expected: `ModuleNotFoundError: No module named 'OrecchietTetris.view.widgets.board_widget'`

- [ ] **Step 3: Create `board_widget.py` with constants and constructor**

Create `OrecchietTetris/view/widgets/board_widget.py`:

```python
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
                rounded_rectangle=(self.x, self.y, self.width, self.height, 20),
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
poetry run pytest tests/view/widgets/test_board_widget.py -v
```

Expected: `PASSED tests/view/widgets/test_board_widget.py::test_board_constants`

- [ ] **Step 5: Type-check and lint**

```bash
poetry run poe mypy && poetry run poe flake8
```

Expected: no errors (new file is fully annotated, lines ≤ 120 chars).

- [ ] **Step 6: Commit**

```bash
git add OrecchietTetris/view/widgets/board_widget.py tests/view/widgets/__init__.py tests/view/widgets/test_board_widget.py
git commit -m "feat(view): add BoardWidget with rendering and animation logic"
```

---

## Task 2: Register `BoardWidget` in `widgets/__init__.py`

**Files:**
- Modify: `OrecchietTetris/view/widgets/__init__.py`

Current content of `OrecchietTetris/view/widgets/__init__.py`:
```python
from OrecchietTetris.view.widgets.cell import Cell
from OrecchietTetris.view.widgets.piece_preview import PiecePreview
from OrecchietTetris.view.widgets.titled_box import TitledBox
from OrecchietTetris.view.widgets.rounded_button import RoundedButton
from OrecchietTetris.view.widgets.rounded_toggle_button import RoundedToggleButton
from OrecchietTetris.view.widgets.dialog_overlay import DialogOverlay

__all__ = ["Cell", "PiecePreview", "TitledBox", "RoundedButton", "RoundedToggleButton", "DialogOverlay"]
```

- [ ] **Step 1: Write the failing test**

Append to `tests/view/widgets/test_board_widget.py`:
```python
def test_board_widget_exported_from_widgets_package():
    from OrecchietTetris.view.widgets import BoardWidget  # noqa: F401
```

- [ ] **Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/view/widgets/test_board_widget.py::test_board_widget_exported_from_widgets_package -v
```

Expected: `ImportError: cannot import name 'BoardWidget'`

- [ ] **Step 3: Update `__init__.py`**

Replace the full content of `OrecchietTetris/view/widgets/__init__.py` with:
```python
from OrecchietTetris.view.widgets.cell import Cell
from OrecchietTetris.view.widgets.piece_preview import PiecePreview
from OrecchietTetris.view.widgets.titled_box import TitledBox
from OrecchietTetris.view.widgets.rounded_button import RoundedButton
from OrecchietTetris.view.widgets.rounded_toggle_button import RoundedToggleButton
from OrecchietTetris.view.widgets.dialog_overlay import DialogOverlay
from OrecchietTetris.view.widgets.board_widget import BoardWidget

__all__ = [
    "Cell",
    "PiecePreview",
    "TitledBox",
    "RoundedButton",
    "RoundedToggleButton",
    "DialogOverlay",
    "BoardWidget",
]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
poetry run pytest tests/view/widgets/test_board_widget.py -v
```

Expected: all tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add OrecchietTetris/view/widgets/__init__.py tests/view/widgets/test_board_widget.py
git commit -m "feat(view): export BoardWidget from widgets package"
```

---

## Task 3: Update `GameScreen` to use `BoardWidget`

**Files:**
- Modify: `OrecchietTetris/view/game_screen.py`

This task removes board construction/rendering/animation code from `GameScreen` and replaces it with `BoardWidget` calls. Do this in sub-steps to keep each change reviewable.

### 3a — Update imports and remove extracted constants

- [ ] **Step 1: Update the import block at the top of `game_screen.py`**

Replace:
```python
from OrecchietTetris.view.widgets import Cell, PiecePreview, TitledBox, RoundedButton, DialogOverlay
```
With:
```python
from OrecchietTetris.view.widgets import (
    Cell, PiecePreview, TitledBox, RoundedButton, DialogOverlay, BoardWidget,
)
from OrecchietTetris.view.widgets.board_widget import BOARD_ROWS, BOARD_COLS, BOARD_PADDING
```

- [ ] **Step 2: Remove the three module-level constants that moved**

Delete these lines from `game_screen.py` (currently after `GAME_SCREEN_BG`):
```python
BOARD_ROWS = 20
BOARD_COLS = 10
...
BOARD_PADDING = 12      # padding + border around the board
```

Keep `CELL_SIZE = 30` and `PANEL_WIDTH = 160` — those are layout concerns that stay in `game_screen.py`.

- [ ] **Step 3: Run existing tests to confirm no regressions**

```bash
poetry run pytest tests/view/ -v
```

Expected: all existing tests pass (no Kivy widget instantiation in these tests).

### 3b — Update `__init__` field declarations

- [ ] **Step 4: Replace board-related field declarations in `GameScreen.__init__`**

In `GameScreen.__init__`, remove these declarations:
```python
self._board_cells: list[list[Cell]] = []
self._clearing_animation: bool = False
```

And replace with:
```python
self._board: BoardWidget
```

Also remove the type annotation stubs:
```python
self._board_container: AnchorLayout
self._board_widget: GridLayout
```

The full `__init__` field section (lines 95–112) should become:
```python
self._keyboard: Any = None
self._overlay: Optional[Widget] = None
self._quit_overlay: Optional[Widget] = None
self._pause_overlay: Optional[Widget] = None
self._board: BoardWidget
self._countdown_overlay: Optional[Widget] = None
self._on_try_again = self.start_with_countdown
self._root: BoxLayout
self._hold_box: TitledBox
self._next_box: TitledBox
self._title_score: Label
self._title_level: Label
self._title_lines: Label
self._build_ui()
```

### 3c — Update `_dispatch`

- [ ] **Step 5: Replace board rendering calls in `_dispatch`**

Replace the entire `_dispatch` method with:
```python
def _dispatch(self, event_type: EventType, data: Any) -> None:
    if event_type == EventType.BOARD_UPDATED:
        if not self._board.is_animating:
            self._board.redraw(
                self._model.board.grid,
                self._model.shadow_row,
                self._model.current_piece,
                self._model.current_col,
            )
    elif event_type == EventType.NEW_PIECE:
        self._update_next_preview()
        if not self._board.is_animating:
            self._board.redraw(
                self._model.board.grid,
                self._model.shadow_row,
                self._model.current_piece,
                self._model.current_col,
            )
    elif event_type == EventType.LINES_CLEARED:
        self._lbl_lines.text = str(self._model.lines_cleared)
        cleared_rows, pre_clear_grid = data
        rows: list[int] = list(cleared_rows)
        snapshot: list[list[int]] = [
            [pre_clear_grid[r][c] for c in range(BOARD_COLS)]
            for r in range(BOARD_ROWS)
        ]
        self._board.animate_line_clear(
            rows,
            snapshot,
            on_done=lambda: self._board.redraw(
                self._model.board.grid,
                self._model.shadow_row,
                self._model.current_piece,
                self._model.current_col,
            ),
        )
    elif event_type == EventType.SCORE_UPDATED:
        self._lbl_score.text = str(self._model.score)
        self._lbl_level.text = str(self._model.level)
    elif event_type == EventType.GAME_OVER:
        self._show_game_over_overlay()
    elif event_type == EventType.PAUSED:
        self._btn_pause.text = ""
        self._show_pause_overlay()
    elif event_type == EventType.RESUMED:
        self._btn_pause.text = ""
        self._dismiss_pause_overlay()
    elif event_type == EventType.HOLD_UPDATED:
        self._update_hold_preview()
```

Also update `update()` — replace:
```python
def update(self, event_type: EventType, data: Any) -> None:
    if event_type == EventType.LINES_CLEARED:
        self._clearing_animation = True
    Clock.schedule_once(lambda dt: self._dispatch(event_type, data))
```
With:
```python
def update(self, event_type: EventType, data: Any) -> None:
    if event_type == EventType.LINES_CLEARED:
        self._board.is_animating = True
    Clock.schedule_once(lambda dt: self._dispatch(event_type, data))
```

### 3d — Delete extracted private methods

- [ ] **Step 6: Delete the four extracted methods from `GameScreen`**

Delete these method definitions entirely (they now live in `BoardWidget`):
- `_render_cell`
- `_redraw_board`
- `_animate_line_clear`
- `_animate_drop`

### 3e — Replace board construction in `_build_ui`

- [ ] **Step 7: Replace the board-construction block in `_build_ui`**

In `_build_ui`, locate the "Centre column: the board" section (currently lines 619–664). Replace everything from `self._board_widget = GridLayout(...)` through `root.add_widget(board_container)` with:

```python
# ----------------------------------------------------------------
# Centre column: the board
# ----------------------------------------------------------------
self._board = BoardWidget(
    renderer=self._renderer,
    rows=BOARD_ROWS,
    cols=BOARD_COLS,
    cell_size=cell_size,
    padding=BOARD_PADDING,
)
root.add_widget(self._board)
```

### 3f — Update `_on_window_resize`

- [ ] **Step 8: Replace manual sizing in `_on_window_resize`**

Replace the current `_on_window_resize` method:
```python
def _on_window_resize(self, _window: Any, _w: int, _h: int) -> None:
    cell_size = self._calc_cell_size()
    board_w = BOARD_COLS * cell_size + (BOARD_COLS - 1)
    board_h = BOARD_ROWS * cell_size + (BOARD_ROWS - 1)
    self._board_widget.size = (board_w, board_h)
    self._board_container.size = (board_w + 2 * BOARD_PADDING, board_h + 2 * BOARD_PADDING)
    self._root.width = board_w + 2 * BOARD_PADDING + 2 * PANEL_WIDTH + 60
    self._root.height = board_h + 2 * BOARD_PADDING + 20
    self._update_bg()
```

With:
```python
def _on_window_resize(self, _window: Any, _w: int, _h: int) -> None:
    cell_size = self._calc_cell_size()
    self._board.resize(cell_size)
    cw, ch = self._board.container_size
    self._root.width = cw + 2 * PANEL_WIDTH + 60
    self._root.height = ch + 20
    self._update_bg()
```

### 3g — Clean up unused imports

- [ ] **Step 9: Remove unused imports from `game_screen.py`**

After the refactor, `GridLayout`, `AnchorLayout`, and `Line` are no longer used directly in `game_screen.py`. Remove them from the Kivy import lines:

Change:
```python
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore[import-untyped]
from kivy.uix.gridlayout import GridLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle  # type: ignore[import-untyped]
```

To:
```python
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle, RoundedRectangle  # type: ignore[import-untyped]
```

Also remove `Cell` from the widgets import since it's no longer directly referenced in `game_screen.py`:
```python
from OrecchietTetris.view.widgets import (
    PiecePreview, TitledBox, RoundedButton, DialogOverlay, BoardWidget,
)
```

- [ ] **Step 10: Also update `_build_ui` layout sizing math**

In `_build_ui`, the `board_w` / `board_h` / `total_width` / `total_height` variables are used for the root `BoxLayout` size. After the refactor, replace:
```python
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
```

With:
```python
cell_size = self._calc_cell_size()
self._board = BoardWidget(
    renderer=self._renderer,
    rows=BOARD_ROWS,
    cols=BOARD_COLS,
    cell_size=cell_size,
    padding=BOARD_PADDING,
)
cw, ch = self._board.container_size
root = BoxLayout(
    orientation="horizontal",
    spacing=20,
    padding=10,
    size_hint=(None, None),
    width=cw + 2 * PANEL_WIDTH + 60,
    height=ch + 20,
)
```

Then remove the duplicate `self._board = BoardWidget(...)` that was placed in the centre-column section in Step 7 (the instantiation now happens before `root` is built). The centre-column section just does `root.add_widget(self._board)`.

- [ ] **Step 11: Run all tests**

```bash
poetry run poe test
```

Expected: all tests pass.

- [ ] **Step 12: Run type check and lint**

```bash
poetry run poe mypy && poetry run poe flake8
```

Expected: no errors.

- [ ] **Step 13: Commit**

```bash
git add OrecchietTetris/view/game_screen.py
git commit -m "refactor(view): use BoardWidget in GameScreen, remove extracted code"
```

---

## Self-Review

**Spec coverage:**
- ✅ `BoardWidget` created in `view/widgets/board_widget.py`
- ✅ Constructor with `renderer`, `rows`, `cols`, `cell_size`, `padding`
- ✅ `is_animating` property (gettable + settable)
- ✅ `board_size` / `container_size` properties
- ✅ `redraw(grid, shadow_row, piece, cur_col)`
- ✅ `animate_line_clear(rows, snapshot, on_done)`
- ✅ `resize(cell_size)`
- ✅ `widgets/__init__.py` updated
- ✅ `GameScreen` fields/methods/imports cleaned up
- ✅ `_on_window_resize` updated
- ✅ `_clearing_animation` replaced by `board.is_animating`
- ✅ Constants `BOARD_ROWS`, `BOARD_COLS`, `BOARD_PADDING` moved; imported back into `game_screen`
- ✅ `CELL_SIZE`, `PANEL_WIDTH` remain in `game_screen.py`

**Threading note:** `GameScreen.update()` sets `self._board.is_animating = True` synchronously (before the Clock callback) when `LINES_CLEARED` arrives. This preserves the original gating behavior that prevents `BOARD_UPDATED` callbacks queued ahead of `LINES_CLEARED` from overwriting cells during animation.

**Placeholder scan:** No TBD, TODO, or vague steps. All code blocks are complete.

**Type consistency:**
- `animate_line_clear` → calls `_animate_flash` internally (not `_animate_line_clear` — consistent throughout)
- `on_done: Optional[Callable[[], None]]` — same signature in declaration, `_animate_flash`, `_animate_drop`, and call sites in `GameScreen`
- `board_size`, `container_size` → `tuple[float, float]` — consistent with Kivy sizing conventions
