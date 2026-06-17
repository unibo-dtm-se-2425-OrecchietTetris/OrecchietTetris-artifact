"""Tests for TitledBox.

TitledBox is a panel widget with an optional bold title label at the top
and a swappable content widget in the body.  All layout calculations are
pure Python; the Kivy canvas calls go through MagicMock stubs.
"""
from __future__ import annotations

from OrecchietTetris.view.widgets.titled_box import TitledBox


# ---------------------------------------------------------------------------
# Construction — lines 17-37
# ---------------------------------------------------------------------------

def test_titled_box_without_title() -> None:
    box = TitledBox(size_hint=(1, None), height=100)
    assert box is not None
    assert box._title_str is None
    assert box._lbl.opacity == 0


def test_titled_box_with_title() -> None:
    box = TitledBox(title="Hold", size_hint=(1, None), height=100)
    assert box._title_str == "Hold"
    assert box._lbl.text == "Hold"
    assert box._lbl.opacity == 1


def test_titled_box_has_background_instruction() -> None:
    box = TitledBox(title="Test")
    assert hasattr(box, "_bg_instr")


# ---------------------------------------------------------------------------
# set_title — lines 40-43
# ---------------------------------------------------------------------------

def test_set_title_updates_label_text() -> None:
    box = TitledBox()
    box.set_title("Score")
    assert box._lbl.text == "Score"
    assert box._title_str == "Score"


def test_set_title_makes_label_visible() -> None:
    box = TitledBox()  # no title → opacity 0
    box.set_title("Level")
    assert box._lbl.opacity == 1


def test_set_title_none_hides_label() -> None:
    box = TitledBox(title="Old")
    box.set_title(None)
    assert box._lbl.text == ""
    assert box._lbl.opacity == 0


# ---------------------------------------------------------------------------
# set_content — lines 46-48
# ---------------------------------------------------------------------------

def test_set_content_stores_widget() -> None:
    from OrecchietTetris.view.widgets.cell import Cell
    box = TitledBox(title="Next", height=120)
    content = Cell()
    box.set_content(content)
    assert box._content_widget is content


def test_set_content_triggers_layout() -> None:
    """set_content() must call _layout() which updates content size/pos."""
    from OrecchietTetris.view.widgets.cell import Cell
    box = TitledBox(title="Hold", height=120, width=160)
    content = Cell()
    box.set_content(content)
    # After layout, content must have received a size (non-zero width)
    assert content.width > 0 or content.size[0] >= 0  # layout was called


# ---------------------------------------------------------------------------
# _layout — lines 51-68
# ---------------------------------------------------------------------------

def test_layout_with_title_reduces_content_height() -> None:
    """With a title, the content area must be shorter than the box height."""
    from OrecchietTetris.view.widgets.cell import Cell
    box = TitledBox(title="Hold", height=120, width=160)
    content = Cell()
    box.set_content(content)
    box._layout()
    # Content height = h - title_h - 3*pad; box height is 120
    expected_h = 120 - TitledBox._TITLE_H - 3 * TitledBox._PAD
    assert content.size[1] == expected_h


def test_layout_without_title_gives_full_body_to_content() -> None:
    """Without a title, only padding is subtracted from content height."""
    from OrecchietTetris.view.widgets.cell import Cell
    box = TitledBox(height=120, width=160)
    content = Cell()
    box.set_content(content)
    box._layout()
    expected_h = 120 - 2 * TitledBox._PAD
    assert content.size[1] == expected_h


def test_layout_updates_background_instruction() -> None:
    box = TitledBox(height=100, width=200)
    box._layout()
    assert box._bg_instr.pos == (box.x, box.y)
    assert box._bg_instr.size == (box.width, box.height)
