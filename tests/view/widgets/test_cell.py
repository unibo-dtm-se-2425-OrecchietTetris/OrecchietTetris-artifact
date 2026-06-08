"""Tests for the Cell widget.

Cell is a single board cell that can show either a solid RGBA colour or a
Kivy texture.  All Kivy canvas calls go to MagicMock stubs (see conftest.py).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from OrecchietTetris.view.block_renderer import EMPTY_COLOUR
from OrecchietTetris.view.widgets.cell import Cell


@pytest.fixture()
def cell() -> Cell:
    return Cell(size_hint=(None, None))


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_cell_can_be_instantiated(cell: Cell) -> None:
    assert cell is not None


def test_cell_has_canvas_instructions(cell: Cell) -> None:
    """After __init__, the four canvas instruction references must exist."""
    assert hasattr(cell, "_color_instr")
    assert hasattr(cell, "_rect")
    assert hasattr(cell, "_img_color")
    assert hasattr(cell, "_img_rect")


# ---------------------------------------------------------------------------
# set_colour — lines 27-29
# ---------------------------------------------------------------------------

def test_set_colour_updates_background_color(cell: Cell) -> None:
    """set_colour() must store the RGBA tuple in the color instruction."""
    rgba = (1.0, 0.0, 0.0, 1.0)
    cell.set_colour(rgba)
    assert cell._color_instr.rgba == rgba


def test_set_colour_hides_image_layer(cell: Cell) -> None:
    """set_colour() must set the image-layer alpha to 0 (invisible)."""
    cell.set_colour((0.5, 0.5, 0.5, 1.0))
    assert cell._img_color.a == 0.0


def test_set_colour_clears_rect_texture(cell: Cell) -> None:
    """set_colour() must clear any previously assigned texture."""
    cell.set_colour((0.0, 1.0, 0.0, 1.0))
    assert cell._rect.texture is None


# ---------------------------------------------------------------------------
# set_texture — lines 32-37
# ---------------------------------------------------------------------------

def test_set_texture_makes_image_layer_opaque_by_default(cell: Cell) -> None:
    tex = MagicMock()
    cell.set_texture(tex)
    assert cell._img_color.rgba == (1.0, 1.0, 1.0, 1.0)


def test_set_texture_respects_alpha_argument(cell: Cell) -> None:
    tex = MagicMock()
    cell.set_texture(tex, alpha=0.35)
    assert cell._img_color.rgba == (1.0, 1.0, 1.0, 0.35)


def test_set_texture_assigns_texture_to_img_rect(cell: Cell) -> None:
    tex = MagicMock()
    cell.set_texture(tex)
    assert cell._img_rect.texture is tex


def test_set_texture_resets_background_to_empty_colour(cell: Cell) -> None:
    """set_texture() must reset the solid background to EMPTY_COLOUR.

    Inject independent MagicMocks so _color_instr and _img_color are distinct
    objects; without this, both share the same Color() return_value and the
    rgba written by _img_color would overwrite the one written by _color_instr.
    """
    cell._color_instr = MagicMock()
    cell._img_color = MagicMock()
    cell._rect = MagicMock()
    cell._img_rect = MagicMock()
    cell.set_texture(MagicMock())
    assert cell._color_instr.rgba == EMPTY_COLOUR


# ---------------------------------------------------------------------------
# _redraw — lines 40-43
# ---------------------------------------------------------------------------

def test_redraw_propagates_current_pos_and_size(cell: Cell) -> None:
    """_redraw() must synchronise both Rectangle instructions with pos/size."""
    new_pos = (50.0, 50.0)
    new_size = (30.0, 30.0)
    cell.pos = new_pos
    cell.size = new_size
    cell._redraw()
    assert cell._rect.pos == new_pos
    assert cell._rect.size == new_size
    assert cell._img_rect.pos == new_pos
    assert cell._img_rect.size == new_size
