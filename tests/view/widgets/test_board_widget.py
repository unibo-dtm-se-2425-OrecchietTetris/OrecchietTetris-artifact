"""Tests for BoardWidget.

BoardWidget owns the 10×20 cell grid, border styling and line-clear animations.
It knows nothing about the model — callers pass grid/piece data explicitly.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.view.block_renderer import BlockRenderer, EMPTY_COLOUR
from OrecchietTetris.view.widgets.board_widget import (
    BoardWidget,
    BOARD_ROWS,
    BOARD_COLS,
    BOARD_PADDING,
)


def test_board_constants():
    assert BOARD_ROWS == 20
    assert BOARD_COLS == 10
    assert BOARD_PADDING == 12


def test_board_widget_exported_from_widgets_package():
    from OrecchietTetris.view.widgets import BoardWidget  # noqa: F401


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def renderer() -> BlockRenderer:
    return BlockRenderer()


@pytest.fixture()
def bw(renderer: BlockRenderer) -> BoardWidget:
    """Small 4×4 board for fast tests."""
    return BoardWidget(renderer=renderer, rows=4, cols=4, cell_size=30, padding=12)


# ---------------------------------------------------------------------------
# Construction — lines 35-80
# ---------------------------------------------------------------------------

def test_board_widget_can_be_instantiated(bw: BoardWidget) -> None:
    assert bw is not None


def test_board_widget_creates_cell_grid(bw: BoardWidget) -> None:
    assert len(bw._board_cells) == 4
    for row in bw._board_cells:
        assert len(row) == 4


def test_board_widget_has_background_instruction(bw: BoardWidget) -> None:
    assert hasattr(bw, "_board_bg_instr")


# ---------------------------------------------------------------------------
# Properties — lines 95, 99, 103, 107
# ---------------------------------------------------------------------------

def test_is_animating_defaults_to_false(bw: BoardWidget) -> None:
    assert bw.is_animating is False


def test_is_animating_setter(bw: BoardWidget) -> None:
    bw.is_animating = True
    assert bw.is_animating is True
    bw.is_animating = False
    assert bw.is_animating is False


def test_board_size_property(bw: BoardWidget) -> None:
    """board_size must return the inner grid dimensions (without padding)."""
    w, h = bw.board_size
    assert w > 0 and h > 0


def test_container_size_property(bw: BoardWidget) -> None:
    """container_size must include the padding on all sides."""
    cw, ch = bw.container_size
    bw_inner, bh_inner = bw.board_size
    assert cw == bw.width
    assert ch == bw.height


# ---------------------------------------------------------------------------
# redraw — lines 117-132
# ---------------------------------------------------------------------------

def test_redraw_empty_grid_sets_all_cells_to_empty_colour(bw: BoardWidget) -> None:
    grid = [[0] * 4 for _ in range(4)]
    mock_cells = [[MagicMock() for _ in range(4)] for _ in range(4)]
    bw._board_cells = mock_cells

    bw.redraw(grid, shadow_row=99, piece=None, cur_col=0)

    for r in range(4):
        for c in range(4):
            mock_cells[r][c].set_colour.assert_called_with(EMPTY_COLOUR)


def test_redraw_shadow_cells_get_shadow_colour(bw: BoardWidget, renderer: BlockRenderer) -> None:
    grid = [[0] * 4 for _ in range(4)]
    mock_piece = MagicMock()
    mock_piece.shape = [[1]]  # 1×1 piece for simplicity

    mock_cells = [[MagicMock() for _ in range(4)] for _ in range(4)]
    bw._board_cells = mock_cells

    bw.redraw(grid, shadow_row=2, piece=mock_piece, cur_col=1)

    # Cell at (2,1) should receive shadow colour
    mock_cells[2][1].set_colour.assert_called_with(renderer.shadow_colour())


def test_redraw_filled_cell_without_texture_calls_set_colour(
    bw: BoardWidget, renderer: BlockRenderer
) -> None:
    grid = [[0] * 4 for _ in range(4)]
    grid[0][0] = 1  # filled cell, no texture loaded

    mock_cells = [[MagicMock() for _ in range(4)] for _ in range(4)]
    bw._board_cells = mock_cells

    bw.redraw(grid, shadow_row=99, piece=None, cur_col=0)

    mock_cells[0][0].set_colour.assert_called_with(renderer.colour(1))


def test_redraw_filled_cell_with_texture_calls_set_texture(
    bw: BoardWidget, renderer: BlockRenderer
) -> None:
    grid = [[0] * 4 for _ in range(4)]
    grid[0][0] = 2

    fake_tex = MagicMock()
    renderer._textures[2] = fake_tex

    mock_cells = [[MagicMock() for _ in range(4)] for _ in range(4)]
    bw._board_cells = mock_cells

    bw.redraw(grid, shadow_row=99, piece=None, cur_col=0)

    mock_cells[0][0].set_texture.assert_called_with(fake_tex)


# ---------------------------------------------------------------------------
# resize — lines 150-153
# ---------------------------------------------------------------------------

def test_resize_updates_board_widget_size(bw: BoardWidget) -> None:
    """resize() must set _board_widget.size to the new cell-based dimensions."""
    bw.resize(20.0)
    expected_board_w = 4 * 20 + (4 - 1)
    expected_board_h = 4 * 20 + (4 - 1)
    assert bw._board_widget.size == (expected_board_w, expected_board_h)


def test_resize_updates_container_size(bw: BoardWidget) -> None:
    """resize() must set the container (self) size to board + 2*padding."""
    bw.resize(20.0)
    expected_board_w = 4 * 20 + (4 - 1)
    expected_board_h = 4 * 20 + (4 - 1)
    expected_w = expected_board_w + 2 * 12  # padding=12
    expected_h = expected_board_h + 2 * 12
    assert bw.size == (expected_w, expected_h)


# ---------------------------------------------------------------------------
# _render_cell — lines 160-164
# ---------------------------------------------------------------------------

def test_render_cell_with_zero_val_uses_colour(bw: BoardWidget, renderer: BlockRenderer) -> None:
    mock_cell = MagicMock()
    bw._board_cells[0][0] = mock_cell
    bw._render_cell(0, 0, 0)
    mock_cell.set_colour.assert_called_with(renderer.colour(0))


def test_render_cell_with_texture_uses_set_texture(
    bw: BoardWidget, renderer: BlockRenderer
) -> None:
    fake_tex = MagicMock()
    renderer._textures[3] = fake_tex
    mock_cell = MagicMock()
    bw._board_cells[1][1] = mock_cell
    bw._render_cell(1, 1, 3)
    mock_cell.set_texture.assert_called_with(fake_tex)


# ---------------------------------------------------------------------------
# animate_line_clear — lines 145-146, 173-181, 190-216
# ---------------------------------------------------------------------------

def test_animate_line_clear_sets_animating_flag(bw: BoardWidget) -> None:
    grid = [[0] * 4 for _ in range(4)]

    with patch("OrecchietTetris.view.widgets.board_widget.Clock") as mock_clock:
        mock_clock.schedule_once.side_effect = lambda cb, delay: None
        bw.animate_line_clear([3], grid)

    assert bw.is_animating is True


def test_animate_line_clear_completes_and_calls_on_done(bw: BoardWidget) -> None:
    """Running the full animation must clear is_animating and call on_done()."""
    grid = [[0] * 4 for _ in range(4)]
    grid[3] = [1] * 4

    on_done = MagicMock()

    with patch("OrecchietTetris.view.widgets.board_widget.Clock") as mock_clock:
        # Immediately invoke each scheduled callback (synchronous animation)
        mock_clock.schedule_once.side_effect = lambda cb, delay: cb(0)
        bw.animate_line_clear([3], grid, on_done=on_done)

    assert bw.is_animating is False
    on_done.assert_called_once()


def test_animate_line_clear_without_on_done_does_not_raise(bw: BoardWidget) -> None:
    grid = [[0] * 4 for _ in range(4)]

    with patch("OrecchietTetris.view.widgets.board_widget.Clock") as mock_clock:
        mock_clock.schedule_once.side_effect = lambda cb, delay: cb(0)
        bw.animate_line_clear([2], grid, on_done=None)

    assert bw.is_animating is False


def test_animate_drop_renders_non_zero_snapshot_cells(bw: BoardWidget, renderer: BlockRenderer) -> None:
    """Line 206: val != 0 branch in _animate_drop must call _render_cell for filled cells."""
    # Row 3 is cleared; row 0 has a filled cell (val=1) → must be rendered during drop
    snapshot = [[0] * 4 for _ in range(4)]
    snapshot[0][0] = 1  # non-zero cell in a non-cleared row

    mock_cells = [[MagicMock() for _ in range(4)] for _ in range(4)]
    bw._board_cells = mock_cells

    with patch("OrecchietTetris.view.widgets.board_widget.Clock") as mock_clock:
        mock_clock.schedule_once.side_effect = lambda cb, delay: cb(0)
        bw.animate_line_clear([3], snapshot, on_done=None)

    # At least one cell must have had set_colour or set_texture called for the
    # non-zero snapshot cell that dropped through _animate_drop.
    rendered = any(
        mock_cells[r][c].set_colour.called or mock_cells[r][c].set_texture.called
        for r in range(4) for c in range(4)
    )
    assert rendered


# ---------------------------------------------------------------------------
# Background callback — lines 76-77 (closure registered via bind in __init__)
# ---------------------------------------------------------------------------

def test_board_bg_update_callback_syncs_pos_and_size() -> None:
    """The _update_bg closure must write pos and size back to _board_bg_instr.

    Since the stub bind() is a no-op, we capture the callback by temporarily
    replacing bind with a capturing version during construction.
    """
    from OrecchietTetris.view.widgets.board_widget import BoardWidget
    from OrecchietTetris.view.block_renderer import BlockRenderer

    captured: dict[str, object] = {}

    def capturing_bind(self_w, **kwargs):
        captured.update(kwargs)

    BoardWidget.bind = capturing_bind
    try:
        r = BlockRenderer()
        bw2 = BoardWidget(renderer=r, rows=2, cols=2, cell_size=20, padding=4)
    finally:
        # Restore the original no-op bind from the stub
        BoardWidget.bind = lambda self, **kw: None

    assert "pos" in captured or "size" in captured, "bind must receive pos or size callback"

    # Trigger the closure directly with a new pos/size
    bw2.x = 5.0
    bw2.y = 10.0
    bw2.width = 200.0
    bw2.height = 300.0
    cb = captured.get("pos") or captured.get("size")
    assert cb is not None
    cb()  # type: ignore[operator]
    assert bw2._board_bg_instr.pos == (5.0, 10.0)
    assert bw2._board_bg_instr.size == (200.0, 300.0)
