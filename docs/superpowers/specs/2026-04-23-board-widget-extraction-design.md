# Design: Extract BoardWidget from GameScreen

**Date:** 2026-04-23
**Branch:** fix/ui

## Summary

Extract board rendering and animation logic from `GameScreen` into a self-contained `BoardWidget(AnchorLayout)` widget in `view/widgets/board_widget.py`. Follows the same pattern as `PiecePreview`: renderer injected, model data passed explicitly via method calls.

## New File

`OrecchietTetris/view/widgets/board_widget.py`

### Class: `BoardWidget(AnchorLayout)`

**Constructor:**
```python
BoardWidget(
    renderer: BlockRenderer,
    rows: int,
    cols: int,
    cell_size: float,
    padding: int,
    **kwargs: Any,
)
```

Builds the `GridLayout` of `Cell` widgets and wraps it in the `AnchorLayout` with a rounded border. All sizing derived from arguments.

### Public API

| Member | Signature | Description |
|---|---|---|
| `is_animating` | `@property -> bool` | `True` while line-clear animation runs |
| `board_size` | `@property -> tuple[float, float]` | `(board_w, board_h)` |
| `container_size` | `@property -> tuple[float, float]` | `(board_w + 2*padding, board_h + 2*padding)` |
| `redraw` | `(grid, shadow_row, piece, cur_col) -> None` | Repaints every cell from board state + ghost shadow |
| `animate_line_clear` | `(rows, snapshot, on_done=None) -> None` | Flash rows white → drop animation → call `on_done()` |
| `resize` | `(cell_size: float) -> None` | Updates GridLayout + container sizes for window resize |

### Internal members moved from GameScreen

- `_board_cells: list[list[Cell]]`
- `_board_border: Line`
- `_clearing_animation: bool` (exposed as `is_animating`)
- `_render_cell(row, col, val)`
- `_redraw_board(grid, shadow_row, piece, cur_col)` → becomes `redraw()`
- `_animate_line_clear(rows, snapshot, idx)` → becomes `animate_line_clear(rows, snapshot, on_done)`
- `_animate_drop(rows, snapshot, step)` → internal, calls `on_done` when complete

### Constants moved into board_widget.py

- `BOARD_ROWS = 20`
- `BOARD_COLS = 10`
- `BOARD_PADDING = 12`

`GameScreen` imports `BOARD_ROWS`, `BOARD_COLS`, `BOARD_PADDING` from `board_widget` so the snapshot loop in `_dispatch` can still reference them without touching widget internals.

## Changes to GameScreen

### Removed
- Fields: `_board_cells`, `_board_widget`, `_board_container`, `_board_border`, `_clearing_animation`
- Methods: `_render_cell`, `_redraw_board`, `_animate_line_clear`, `_animate_drop`
- Constants: `BOARD_ROWS`, `BOARD_COLS`, `BOARD_PADDING` (now imported from `board_widget`)

### Added
- Field: `_board: BoardWidget`

### Modified

**`_build_ui`** — board-construction block (~40 lines, currently lines 622–664) replaced by:
```python
cell_size = self._calc_cell_size()
self._board = BoardWidget(
    renderer=self._renderer,
    rows=BOARD_ROWS,
    cols=BOARD_COLS,
    cell_size=cell_size,
    padding=BOARD_PADDING,
)
root.add_widget(self._board)
```

**`_dispatch`** — replace direct cell/flag access:
```python
# BOARD_UPDATED
if not self._board.is_animating:
    self._board.redraw(
        self._model.board.grid,
        self._model.shadow_row,
        self._model.current_piece,
        self._model.current_col,
    )

# LINES_CLEARED
cleared_rows, pre_clear_grid = data
self._board.animate_line_clear(
    list(cleared_rows),
    [[pre_clear_grid[r][c] for c in range(BOARD_COLS)] for r in range(BOARD_ROWS)],
    on_done=self._board.redraw.__func__,  # actually just call redraw in on_done
)

# NEW_PIECE
self._update_next_preview()
if not self._board.is_animating:
    self._board.redraw(...)
```

**`_on_window_resize`** — replace manual sizing:
```python
self._board.resize(cell_size)
self._root.width = self._board.container_size[0] + 2 * PANEL_WIDTH + 60
self._root.height = self._board.container_size[1] + 20
```

## Changes to widgets/__init__.py

Add import and `__all__` entry:
```python
from OrecchietTetris.view.widgets.board_widget import BoardWidget
__all__ = [..., "BoardWidget"]
```

## Architecture

```
view/widgets/board_widget.py   BoardWidget(AnchorLayout)
    uses: Cell, BlockRenderer, BLOCK_COLOURS
    knows: rows/cols/padding/cell_size (construction), grid/shadow/piece (per-draw call)
    does NOT know: ITetris, GameScreen, EventType

view/game_screen.py            GameScreen
    owns: BoardWidget instance
    passes: model data to BoardWidget methods
    checks: board.is_animating before calling board.redraw()
```

## Constraints

- `CELL_SIZE` and `PANEL_WIDTH` stay in `game_screen.py` — they are layout concerns, not board rendering concerns.
- `animate_line_clear` sets `is_animating = True` on entry and `False` at the end of `_animate_drop`. `GameScreen` does not touch this flag.
- `on_done` callback in `animate_line_clear` is called after drop animation completes. `GameScreen` passes a lambda that calls `self._board.redraw(...)` with fresh model state.
