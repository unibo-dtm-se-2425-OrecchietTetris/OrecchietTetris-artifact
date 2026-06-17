"""Inject lightweight Kivy stubs before any view module is imported.

All view modules import Kivy at the top level.  Since Kivy is not installed
in the test venv, we pre-populate sys.modules with minimal stand-ins so that
imports succeed and widget constructors can be called without a real Kivy/SDL2
environment.

Widget stub classes provide:
- __init__ that sets up canvas, pos, size and stores kwargs as attributes
- bind / add_widget / remove_widget as no-ops
- setter() returning a MagicMock (used by BoxLayout.bind(minimum_height=...) calls)
"""
from __future__ import annotations

import sys
from abc import ABCMeta
from typing import Any
from unittest.mock import MagicMock

import pytest


def _cls(name: str) -> type:
    """Return an ABCMeta-metaclassed stub class usable as a Kivy base class.

    i_view.py does ``type(Screen)`` on the imported Screen stub to derive a
    combined metaclass.  If the stub's metaclass is plain ``type``, combining
    it with ``ABCMeta`` produces an unresolvable MRO.  Using ``ABCMeta`` here
    makes ``issubclass(type(stub), ABCMeta)`` true, so i_view.py takes its
    safe else-branch and sets ``_IViewMeta = ABCMeta`` instead of trying to
    merge ``type`` with ``ABCMeta``.

    The __init__ sets up a MagicMock canvas (which acts as a context manager
    automatically) and stores all kwargs as instance attributes so that code
    like ``Label(text='hi').text`` works in tests.
    """

    def __init__(self: Any, *args: Any, **kwargs: Any) -> None:
        self.canvas = MagicMock()
        self.canvas.before = MagicMock()
        self.canvas.after = MagicMock()
        # Common positional/size attributes
        self.pos = kwargs.get("pos", (0.0, 0.0))
        self.size = kwargs.get("size", (100.0, 100.0))
        self.x = 0.0
        self.y = 0.0
        self.width = float(kwargs.get("width", 100))
        self.height = float(kwargs.get("height", 100))
        self.opacity = kwargs.get("opacity", 1.0)
        self.disabled = kwargs.get("disabled", False)
        self.children = []
        # Default text / state attributes needed by Label / TextInput / Buttons
        self.text = kwargs.get("text", "")
        self.state = kwargs.get("state", "normal")
        # Store every remaining kwarg so widgets can read back their own props
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def bind(self: Any, **kwargs: Any) -> None:
        pass

    def add_widget(self: Any, *args: Any, **kwargs: Any) -> None:
        pass

    def remove_widget(self: Any, *args: Any, **kwargs: Any) -> None:
        pass

    def clear_widgets(self: Any, *args: Any, **kwargs: Any) -> None:
        pass

    def on_touch_down(self: Any, touch: Any) -> bool:
        return False

    def on_touch_move(self: Any, touch: Any) -> bool:
        return False

    def on_touch_up(self: Any, touch: Any) -> bool:
        return False

    def setter(self: Any, attr_name: str) -> MagicMock:
        return MagicMock()

    return ABCMeta(name, (object,), {
        "__init__": __init__,
        "bind": bind,
        "add_widget": add_widget,
        "remove_widget": remove_widget,
        "clear_widgets": clear_widgets,
        "on_touch_down": on_touch_down,
        "on_touch_move": on_touch_move,
        "on_touch_up": on_touch_up,
        "setter": setter,
    })


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
    "kivy.core.image":        MagicMock(),
    "kivy.metrics":           MagicMock(),
    "kivy.properties":        MagicMock(),
    "kivy.lang":              MagicMock(),
}

for _mod_name, _stub in _STUBS.items():
    sys.modules.setdefault(_mod_name, _stub)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# i18n setup — configure the real python-i18n library with English locale
# before every view test so that i18n.t("key") calls inside widget/screen
# constructors resolve to actual strings rather than raising.
# ---------------------------------------------------------------------------

import i18n as _i18n  # type: ignore[import-untyped]  # noqa: E402
from OrecchietTetris.utils.paths import LOCALES_DIR as _LOCALES_DIR  # noqa: E402


@pytest.fixture(autouse=True)
def _configure_i18n() -> Any:
    """Set up python-i18n with English locale for every view test."""
    _i18n.set("file_format", "yml")
    _i18n.set("filename_format", "{locale}.{format}")
    _i18n.set("load_path", [str(_LOCALES_DIR)])
    _i18n.set("locale", "en")
    _i18n.set("fallback", "en")
    yield
    # Restore English after each test so locale changes don't bleed between tests.
    _i18n.set("locale", "en")
