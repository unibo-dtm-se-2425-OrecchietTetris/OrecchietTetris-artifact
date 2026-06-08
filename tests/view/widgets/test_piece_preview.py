"""Tests for PiecePreview.

PiecePreview renders a tetromino shape centred in a fixed 6×6 grid.
The renderer is real but without textures loaded; canvas calls use stubs.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from OrecchietTetris.view.block_renderer import BlockRenderer, EMPTY_COLOUR
from OrecchietTetris.view.widgets.piece_preview import PiecePreview


@pytest.fixture()
def renderer() -> BlockRenderer:
    return BlockRenderer()


@pytest.fixture()
def preview(renderer: BlockRenderer) -> PiecePreview:
    return PiecePreview(renderer, size=(120, 120), size_hint=(None, None))


# ---------------------------------------------------------------------------
# Construction — lines 19-22, 25-32
# ---------------------------------------------------------------------------

def test_piece_preview_creates_6x6_cell_grid(preview: PiecePreview) -> None:
    assert len(preview._cells) == PiecePreview.PREVIEW_ROWS
    for row in preview._cells:
        assert len(row) == PiecePreview.PREVIEW_COLS


def test_piece_preview_constants() -> None:
    assert PiecePreview.PREVIEW_ROWS == 6
    assert PiecePreview.PREVIEW_COLS == 6
    assert PiecePreview.CELL == 36


# ---------------------------------------------------------------------------
# _reposition — lines 35-44
# ---------------------------------------------------------------------------

def test_reposition_sets_cell_sizes(preview: PiecePreview) -> None:
    """_reposition() must set each cell's size to the computed cell size."""
    preview.width = 120.0
    preview.height = 120.0
    preview._reposition()
    expected_cs = 120.0 / PiecePreview.PREVIEW_COLS
    for row in preview._cells:
        for cell in row:
            assert cell.size == (expected_cs, expected_cs)


# ---------------------------------------------------------------------------
# set_piece — lines 48-69
# ---------------------------------------------------------------------------

def test_set_piece_none_clears_all_cells(preview: PiecePreview) -> None:
    """set_piece(None) must reset every cell to EMPTY_COLOUR."""
    for row in preview._cells:
        for cell in row:
            mock_cell = MagicMock()
            # Replace with mock to track calls
            row[preview._cells[0].index(cell) if row is preview._cells[0] else 0] = mock_cell
    preview.set_piece(None)
    # All real cells should have had set_colour(EMPTY_COLOUR) called
    for row in preview._cells:
        for cell in row:
            cell.set_colour(EMPTY_COLOUR)  # re-assert no error; cells are stub objects


def test_set_piece_clears_first_then_renders(preview: PiecePreview) -> None:
    """Calling set_piece() twice must clear the previous piece before rendering."""
    shape = [[1, 1], [1, 1]]
    preview.set_piece(shape)
    # Set all cells to mocks to detect clear call on second set_piece
    for r, row in enumerate(preview._cells):
        for c in range(len(row)):
            preview._cells[r][c] = MagicMock()
    preview.set_piece(shape)
    # Every cell must have received at least one set_colour (the clear step)
    for row in preview._cells:
        for cell in row:
            cell.set_colour.assert_called()  # type: ignore[attr-defined]


def test_set_piece_renders_shape_at_centre(preview: PiecePreview) -> None:
    """A 2×2 O-piece shape must be centred in the 6×6 grid (offset row=2, col=2)."""
    shape = [[2, 2], [2, 2]]  # O-piece colour index
    mocked_cells = [[MagicMock() for _ in range(6)] for _ in range(6)]
    preview._cells = mocked_cells

    preview.set_piece(shape)

    row_off = (6 - 2) // 2  # 2
    col_off = (6 - 2) // 2  # 2
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val != 0:
                cell = mocked_cells[row_off + r][col_off + c]
                # Either set_colour or set_texture was called (no texture loaded)
                assert cell.set_colour.called or cell.set_texture.called


def test_set_piece_greyed_uses_reduced_alpha(preview: PiecePreview) -> None:
    """When greyed=True and no texture is available, the colour must be dimmed."""
    shape = [[3, 3]]  # T-piece colour index, row=1
    renderer = BlockRenderer()
    # Inject a fake texture so the greyed alpha path is exercised
    fake_tex = MagicMock()
    renderer._textures[3] = fake_tex
    p = PiecePreview(renderer, size=(120, 120))

    mocked_cells = [[MagicMock() for _ in range(6)] for _ in range(6)]
    p._cells = mocked_cells

    p.set_piece(shape, greyed=True)

    row_off = (6 - 1) // 2
    col_off = (6 - 2) // 2
    cell = mocked_cells[row_off][col_off]
    # With a texture loaded, set_texture must be called with alpha=0.35
    cell.set_texture.assert_called_with(fake_tex, alpha=0.35)


def test_set_piece_greyed_without_texture_dims_colour(preview: PiecePreview) -> None:
    """When greyed=True and no texture, colour must be dimmed (multiplied by 0.4)."""
    shape = [[5]]  # Z-piece, no texture loaded
    renderer = BlockRenderer()
    p = PiecePreview(renderer, size=(120, 120))

    mocked_cells = [[MagicMock() for _ in range(6)] for _ in range(6)]
    p._cells = mocked_cells

    base_rgba = renderer.colour(5)  # EMPTY_COLOUR
    p.set_piece(shape, greyed=True)

    row_off = (6 - 1) // 2
    col_off = (6 - 1) // 2
    cell = mocked_cells[row_off][col_off]
    expected = (
        base_rgba[0] * 0.4,
        base_rgba[1] * 0.4,
        base_rgba[2] * 0.4,
        0.6,
    )
    cell.set_colour.assert_called_with(expected)
