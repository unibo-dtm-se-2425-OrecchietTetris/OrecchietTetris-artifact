"""Tests for the IView abstract interface."""
import pytest
from OrecchietTetris.view.interfaces import IView
from OrecchietTetris.utils import EventType


def test_iview_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        IView()  # type: ignore[abstract]


def test_concrete_iview_must_implement_show_hide_update():
    """A minimal concrete class must implement all three abstract methods."""

    class MinimalView(IView):
        def show(self) -> None:
            pass

        def hide(self) -> None:
            pass

        def update(self, event_type: EventType, data: object) -> None:
            pass

    view = MinimalView()
    view.show()
    view.hide()
    view.update(EventType.GAME_OVER, None)


def test_partial_implementation_raises():
    """A class missing one abstract method must still raise TypeError."""

    class Incomplete(IView):
        def show(self) -> None:
            pass

        def hide(self) -> None:
            pass
        # update() not implemented

    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]
