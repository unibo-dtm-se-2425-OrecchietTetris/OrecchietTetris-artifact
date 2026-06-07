"""Inject lightweight Kivy stubs before any view module is imported.

All view modules import Kivy at the top level.  Since Kivy is not installed
in the test venv, we pre-populate sys.modules with minimal stand-ins so that
imports succeed without needing a real Kivy / SDL2 environment.

Only attribute accesses that happen at *import time* (class definitions and
module-level constants) need to work.  Widget constructors are never called
in these tests.
"""
from __future__ import annotations

import sys
from abc import ABCMeta
from unittest.mock import MagicMock


def _cls(name: str) -> type:
    """Return an ABCMeta-metaclassed stub class usable as a Kivy base class.

    i_view.py does ``type(Screen)`` on the imported Screen stub to derive a
    combined metaclass.  If the stub's metaclass is plain ``type``, combining
    it with ``ABCMeta`` produces an unresolvable MRO.  Using ``ABCMeta`` here
    makes ``issubclass(type(stub), ABCMeta)`` true, so i_view.py takes its
    safe else-branch and sets ``_IViewMeta = ABCMeta`` instead of trying to
    merge ``type`` with ``ABCMeta``.
    """
    return ABCMeta(name, (), {})


# Every name that appears as a base class in a view module must be a real
# Python type; anything only called at runtime can remain a MagicMock.
_STUBS: dict[str, object] = {
    "kivy":                   MagicMock(),
    "kivy.uix":               MagicMock(),
    "kivy.uix.widget":        MagicMock(Widget=_cls("Widget")),
    "kivy.uix.boxlayout":     MagicMock(BoxLayout=_cls("BoxLayout")),
    "kivy.uix.gridlayout":    MagicMock(GridLayout=_cls("GridLayout")),
    "kivy.uix.floatlayout":   MagicMock(FloatLayout=_cls("FloatLayout")),
    "kivy.uix.anchorlayout":  MagicMock(AnchorLayout=_cls("AnchorLayout")),
    "kivy.uix.label":         MagicMock(Label=_cls("Label")),
    "kivy.uix.button":        MagicMock(Button=_cls("Button")),
    "kivy.uix.togglebutton":  MagicMock(ToggleButton=_cls("ToggleButton")),
    "kivy.uix.image":         MagicMock(Image=_cls("Image")),
    "kivy.uix.scrollview":    MagicMock(ScrollView=_cls("ScrollView")),
    "kivy.uix.slider":        MagicMock(Slider=_cls("Slider")),
    "kivy.uix.textinput":     MagicMock(TextInput=_cls("TextInput")),
    "kivy.uix.screenmanager": MagicMock(
        Screen=_cls("Screen"),
        ScreenManager=_cls("ScreenManager"),
        NoTransition=MagicMock(),
    ),
    "kivy.graphics":          MagicMock(
        Color=MagicMock(),
        Rectangle=MagicMock(),
        RoundedRectangle=MagicMock(),
        Line=MagicMock(),
    ),
    "kivy.app":               MagicMock(App=_cls("App")),
    "kivy.clock":             MagicMock(),
    "kivy.core":              MagicMock(),
    "kivy.core.text":         MagicMock(LabelBase=MagicMock()),
    "kivy.core.window":       MagicMock(),
    "kivy.core.audio":        MagicMock(),
    "kivy.metrics":           MagicMock(),
    "kivy.properties":        MagicMock(),
    "kivy.lang":              MagicMock(),
}

for _mod_name, _stub in _STUBS.items():
    sys.modules.setdefault(_mod_name, _stub)  # type: ignore[arg-type]
