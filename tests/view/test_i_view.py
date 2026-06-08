"""Tests for the IView abstract interface."""
from __future__ import annotations

import sys
import types
from abc import ABCMeta

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


# ---------------------------------------------------------------------------
# Metaclass resolution paths — lines 21 and 25-27
# ---------------------------------------------------------------------------

def test_iview_metaclass_combined_when_kivy_screen_has_non_abcmeta_metaclass() -> None:
    """When Screen's metaclass is plain type (not ABCMeta), _IViewMeta must be
    a combined metaclass that is a subclass of both type and ABCMeta (line 21).

    This path arises in a real Kivy environment where Screen uses Kivy's C
    MetaEventDispatcher rather than ABCMeta.
    """
    # A Screen whose metaclass is a subclass of `type` but NOT ABCMeta — this
    # mirrors the real Kivy runtime where Screen uses MetaEventDispatcher.
    # We cannot use bare `type` because combining (type, ABCMeta) would violate
    # the MRO (ABCMeta inherits from type, so type cannot appear before it).
    KivyLikeMeta = type("KivyLikeMeta", (type,), {})
    PlainScreen = KivyLikeMeta("Screen", (), {})
    mock_sm = types.SimpleNamespace(Screen=PlainScreen)

    # Remove cached module to force reimport with our custom stub
    old_module = sys.modules.pop("OrecchietTetris.view.interfaces.i_view", None)
    old_sm = sys.modules.get("kivy.uix.screenmanager")
    sys.modules["kivy.uix.screenmanager"] = mock_sm  # type: ignore[assignment]

    try:
        import importlib
        import OrecchietTetris.view.interfaces.i_view as fresh
        importlib.reload(fresh)
        meta = fresh._IViewMeta
        # The combined metaclass must be a subclass of ABCMeta to support @abstractmethod
        assert issubclass(meta, ABCMeta)
    finally:
        # Restore original state so subsequent tests are unaffected
        if old_module is not None:
            sys.modules["OrecchietTetris.view.interfaces.i_view"] = old_module
        else:
            sys.modules.pop("OrecchietTetris.view.interfaces.i_view", None)
        if old_sm is not None:
            sys.modules["kivy.uix.screenmanager"] = old_sm


def test_iview_metaclass_fallback_to_abcmeta_when_kivy_not_importable() -> None:
    """When Screen cannot be imported, _IViewMeta must fall back to plain ABCMeta
    (lines 25-27) so that IView can still be used in headless test environments.
    """
    # Make Screen import fail by providing a namespace without Screen
    missing_screen_mod = types.SimpleNamespace()

    old_module = sys.modules.pop("OrecchietTetris.view.interfaces.i_view", None)
    old_sm = sys.modules.get("kivy.uix.screenmanager")
    # SimpleNamespace has no Screen → ImportError when `from ... import Screen`
    sys.modules["kivy.uix.screenmanager"] = missing_screen_mod  # type: ignore[assignment]

    try:
        import importlib
        import OrecchietTetris.view.interfaces.i_view as fresh
        importlib.reload(fresh)
        assert fresh._IViewMeta is ABCMeta
    finally:
        if old_module is not None:
            sys.modules["OrecchietTetris.view.interfaces.i_view"] = old_module
        else:
            sys.modules.pop("OrecchietTetris.view.interfaces.i_view", None)
        if old_sm is not None:
            sys.modules["kivy.uix.screenmanager"] = old_sm
