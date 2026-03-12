from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from OrecchietTetris.utils import Observer, EventType


class IView(Observer, ABC):
    """Abstract base class for all view components.

    Inherits from ``Observer`` so every view can receive game events
    via ``update(event_type, data)``.  Concrete views must also implement
    ``show()`` and ``hide()`` to control their visibility.
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
