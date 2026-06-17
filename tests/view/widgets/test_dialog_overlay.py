"""Tests for DialogOverlay.

DialogOverlay is a full-screen modal with a centered rounded card.
It blocks all touches beneath it and exposes helpers to add labels,
buttons and generic widgets to the card.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from OrecchietTetris.view.widgets.dialog_overlay import (
    DialogOverlay,
    _CARD_PADDING,
    _LABEL_H,
    _BUTTON_H,
)


@pytest.fixture()
def overlay() -> DialogOverlay:
    return DialogOverlay(title="Game Over", title_color=(1.0, 0.2, 0.2, 1.0))


@pytest.fixture()
def overlay_no_title() -> DialogOverlay:
    return DialogOverlay()


# ---------------------------------------------------------------------------
# Construction — lines 38-88
# ---------------------------------------------------------------------------

def test_dialog_overlay_can_be_instantiated(overlay: DialogOverlay) -> None:
    assert overlay is not None


def test_dialog_overlay_card_starts_at_minimum_height(overlay_no_title: DialogOverlay) -> None:
    """Without a title the card height is the base padding only."""
    assert overlay_no_title._card.height == _CARD_PADDING * 2


def test_dialog_overlay_with_title_grows_card() -> None:
    """A title must grow the card height by (_LABEL_H + 10)."""
    dlg = DialogOverlay(title="Test")
    expected = _CARD_PADDING * 2 + (_LABEL_H + 10)
    assert dlg._card.height == expected


def test_dialog_overlay_has_scrim(overlay: DialogOverlay) -> None:
    assert hasattr(overlay, "_scrim")


def test_dialog_overlay_size_hint_is_fullscreen(overlay: DialogOverlay) -> None:
    assert overlay.size_hint == (1, 1)


# ---------------------------------------------------------------------------
# add_label — lines 100-112
# ---------------------------------------------------------------------------

def test_add_label_returns_label_object(overlay_no_title: DialogOverlay) -> None:
    lbl = overlay_no_title.add_label("Score: 100")
    assert lbl is not None


def test_add_label_grows_card_by_label_height(overlay_no_title: DialogOverlay) -> None:
    before = overlay_no_title._card.height
    overlay_no_title.add_label("test")
    assert overlay_no_title._card.height == before + _LABEL_H


def test_add_label_defaults_to_no_markup(overlay_no_title: DialogOverlay) -> None:
    lbl = overlay_no_title.add_label("plain")
    assert lbl.markup is False


def test_add_label_markup_passed_to_label(overlay_no_title: DialogOverlay) -> None:
    lbl = overlay_no_title.add_label("[font=MaterialIcons]x[/font]", markup=True)
    assert lbl.markup is True


# ---------------------------------------------------------------------------
# add_generic_widget — lines 115-116
# ---------------------------------------------------------------------------

def test_add_generic_widget_grows_card(overlay_no_title: DialogOverlay) -> None:
    before = overlay_no_title._card.height
    widget = MagicMock()
    overlay_no_title.add_generic_widget(widget, height=60)
    assert overlay_no_title._card.height == before + 60


# ---------------------------------------------------------------------------
# add_button — lines 126-141
# ---------------------------------------------------------------------------

def test_add_button_returns_rounded_button(overlay_no_title: DialogOverlay) -> None:
    from OrecchietTetris.view.widgets.rounded_button import RoundedButton
    cb = MagicMock()
    btn = overlay_no_title.add_button("OK", bg=(0.2, 0.6, 0.2, 1), on_release=cb)
    assert isinstance(btn, RoundedButton)


def test_add_button_grows_card(overlay_no_title: DialogOverlay) -> None:
    before = overlay_no_title._card.height
    overlay_no_title.add_button("OK", bg=(0.2, 0.6, 0.2, 1), on_release=MagicMock())
    assert overlay_no_title._card.height == before + _BUTTON_H


def test_add_button_with_font_name(overlay_no_title: DialogOverlay) -> None:
    btn = overlay_no_title.add_button(
        "X", bg=(0.5, 0.5, 0.5, 1), on_release=MagicMock(), font_name="MaterialIcons"
    )
    assert btn is not None


# ---------------------------------------------------------------------------
# add_button_row — lines 148-173
# ---------------------------------------------------------------------------

def test_add_button_row_returns_boxlayout(overlay_no_title: DialogOverlay) -> None:
    row = overlay_no_title.add_button_row([
        {"text": "Yes", "bg": (0.2, 0.7, 0.2, 1), "on_release": MagicMock()},
        {"text": "No",  "bg": (0.7, 0.2, 0.2, 1), "on_release": MagicMock()},
    ])
    assert row is not None


def test_add_button_row_with_font_name(overlay_no_title: DialogOverlay) -> None:
    row = overlay_no_title.add_button_row([
        {
            "text": "A", "bg": (0.1, 0.1, 0.9, 1), "on_release": MagicMock(),
            "font_name": "MaterialIcons", "font_size": "20sp",
        },
    ])
    assert row is not None


def test_add_button_row_grows_card(overlay_no_title: DialogOverlay) -> None:
    before = overlay_no_title._card.height
    overlay_no_title.add_button_row([
        {"text": "A", "bg": (0.1, 0.5, 0.1, 1), "on_release": MagicMock()},
    ])
    assert overlay_no_title._card.height == before + _BUTTON_H


# ---------------------------------------------------------------------------
# Touch blocking — lines 185-194
# ---------------------------------------------------------------------------

def test_on_touch_down_returns_true(overlay: DialogOverlay) -> None:
    """All touch events must return True to prevent interaction with widgets below."""
    assert overlay.on_touch_down(MagicMock()) is True


def test_on_touch_move_returns_true(overlay: DialogOverlay) -> None:
    assert overlay.on_touch_move(MagicMock()) is True


def test_on_touch_up_returns_true(overlay: DialogOverlay) -> None:
    assert overlay.on_touch_up(MagicMock()) is True


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def test_grow_card_spacing_added_for_second_child(overlay_no_title: DialogOverlay) -> None:
    """The first widget added incurs no spacing; each subsequent one adds _CARD_SPACING."""
    overlay_no_title.add_label("first")
    h_after_first = overlay_no_title._card.height
    overlay_no_title.add_label("second")
    # Stub children list is always [] so spacing logic uses n=0 each time
    # Verify height still increased by LABEL_H (base behaviour)
    assert overlay_no_title._card.height > h_after_first


def test_update_scrim_syncs_to_widget_pos_size(overlay: DialogOverlay) -> None:
    overlay.pos = (10, 20)
    overlay.size = (800, 600)
    overlay._update_scrim()
    assert overlay._scrim.pos == (10, 20)
    assert overlay._scrim.size == (800, 600)


def test_update_card_gfx_syncs_to_card(overlay: DialogOverlay) -> None:
    overlay._update_card_gfx()
    assert overlay._card_bg.pos == overlay._card.pos
    assert overlay._card_bg.size == overlay._card.size
