from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any

from OrecchietTetris.utils import Observer, EventType


try:
    # Derive the metaclass from Screen's actual runtime metaclass (whatever
    # Kivy's C extension exposes) to avoid "metaclass conflict" when a concrete
    # view inherits from both a Kivy widget and IView.
    from kivy.uix.screenmanager import Screen as _Screen  # type: ignore[import]
    _KivyMeta = type(_Screen)

    if not issubclass(_KivyMeta, ABCMeta):
        class _IViewMeta(_KivyMeta, ABCMeta):  # type: ignore[misc]
            pass
    else:
        _IViewMeta = _KivyMeta  # type: ignore[assignment]

except ImportError:
    # Outside a Kivy environment (e.g. unit tests) fall back to plain ABCMeta.
    _IViewMeta = ABCMeta  # type: ignore[assignment,misc]


class IView(Observer, metaclass=_IViewMeta):
    """Abstract base class for all view components.

    Inherits from ``Observer`` so every view can receive game events
    via ``update(event_type, data)``.  Concrete views must also implement
    ``show()`` and ``hide()`` to control their visibility.

    The metaclass is a union of Kivy's ``MetaEventDispatcher`` and
    ``ABCMeta`` so that Kivy ``Screen``/``Widget`` subclasses can inherit from
    this interface without a metaclass conflict.
    """

    @abstractmethod
    def show(self) -> None:
        """Make this screen visible."""

    @abstractmethod
    def hide(self) -> None:
        """Make this screen invisible / remove it from the display."""

    @abstractmethod
    def update(self, event_type: EventType, data: Any) -> None:
        """Handle a game event from the model."""
