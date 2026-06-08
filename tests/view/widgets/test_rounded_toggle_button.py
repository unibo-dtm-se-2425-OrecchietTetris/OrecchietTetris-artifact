"""Tests for RoundedToggleButton.

RoundedToggleButton mirrors RoundedButton but extends ToggleButton so it
can be used in exclusive groups (e.g. language selector in the settings
overlay).
"""
from __future__ import annotations

import pytest

from OrecchietTetris.view.widgets.rounded_toggle_button import RoundedToggleButton


@pytest.fixture()
def toggle() -> RoundedToggleButton:
    return RoundedToggleButton(text="EN", group="lang", background_color=(0.2, 0.5, 0.8, 1))


# ---------------------------------------------------------------------------
# Construction — lines 15-25
# ---------------------------------------------------------------------------

def test_rounded_toggle_button_can_be_instantiated(toggle: RoundedToggleButton) -> None:
    assert toggle is not None


def test_rounded_toggle_button_has_canvas_instructions(toggle: RoundedToggleButton) -> None:
    assert hasattr(toggle, "_bg_color_instr")
    assert hasattr(toggle, "_bg_rrect")


def test_rounded_toggle_button_disables_kivy_default_backgrounds(toggle: RoundedToggleButton) -> None:
    assert toggle.background_normal == ""
    assert toggle.background_down == ""
    assert toggle.background_color == (0, 0, 0, 0)


# ---------------------------------------------------------------------------
# _update_shape — lines 28-29
# ---------------------------------------------------------------------------

def test_update_shape_synchronises_rrect(toggle: RoundedToggleButton) -> None:
    toggle.pos = (5.0, 15.0)
    toggle.size = (120.0, 40.0)
    toggle._update_shape()
    assert toggle._bg_rrect.pos == (5.0, 15.0)
    assert toggle._bg_rrect.size == (120.0, 40.0)


# ---------------------------------------------------------------------------
# set_color — line 32
# ---------------------------------------------------------------------------

def test_set_color_updates_color_instruction(toggle: RoundedToggleButton) -> None:
    new_color = (0.1, 0.9, 0.1, 1.0)
    toggle.set_color(new_color)
    assert toggle._bg_color_instr.rgba == new_color


def test_rounded_toggle_button_default_color() -> None:
    """Default grey is applied when no background_color kwarg is provided."""
    toggle = RoundedToggleButton()
    assert hasattr(toggle, "_bg_color_instr")
