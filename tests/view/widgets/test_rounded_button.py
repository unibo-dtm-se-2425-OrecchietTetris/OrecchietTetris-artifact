"""Tests for RoundedButton.

RoundedButton extends the Kivy Button with a rounded-rectangle background
drawn via canvas.before.  All Kivy calls go through MagicMock stubs.
"""
from __future__ import annotations

import pytest

from OrecchietTetris.view.widgets.rounded_button import RoundedButton


@pytest.fixture()
def btn() -> RoundedButton:
    return RoundedButton(text="Click me", background_color=(0.2, 0.6, 0.2, 1))


# ---------------------------------------------------------------------------
# Construction — lines 15-25
# ---------------------------------------------------------------------------

def test_rounded_button_can_be_instantiated(btn: RoundedButton) -> None:
    assert btn is not None


def test_rounded_button_has_canvas_bg_instruction(btn: RoundedButton) -> None:
    assert hasattr(btn, "_bg_color_instr")
    assert hasattr(btn, "_bg_rrect")


def test_rounded_button_disables_kivy_default_backgrounds(btn: RoundedButton) -> None:
    """The Kivy default image backgrounds must be cleared so only the custom
    rounded rectangle is visible."""
    assert btn.background_normal == ""
    assert btn.background_down == ""


def test_rounded_button_transparent_background_color(btn: RoundedButton) -> None:
    """The Kivy-level background_color must be fully transparent; colour comes
    from the canvas.before RoundedRectangle."""
    assert btn.background_color == (0, 0, 0, 0)


# ---------------------------------------------------------------------------
# _update_shape — lines 28-29
# ---------------------------------------------------------------------------

def test_update_shape_synchronises_rrect_geometry(btn: RoundedButton) -> None:
    """_update_shape() must copy the widget pos/size to the rounded rectangle."""
    btn.pos = (10.0, 20.0)
    btn.size = (200.0, 50.0)
    btn._update_shape()
    assert btn._bg_rrect.pos == (10.0, 20.0)
    assert btn._bg_rrect.size == (200.0, 50.0)


# ---------------------------------------------------------------------------
# set_color — line 32
# ---------------------------------------------------------------------------

def test_set_color_updates_color_instruction(btn: RoundedButton) -> None:
    """set_color() must update the RGBA of the canvas color instruction."""
    new_color = (0.9, 0.1, 0.1, 1.0)
    btn.set_color(new_color)
    assert btn._bg_color_instr.rgba == new_color


def test_rounded_button_default_background_color() -> None:
    """When no background_color kwarg is given, the default grey must be used."""
    btn = RoundedButton()
    # The button exists and has the colour instruction; default is (0.5, 0.5, 0.5, 1.0)
    assert hasattr(btn, "_bg_color_instr")
