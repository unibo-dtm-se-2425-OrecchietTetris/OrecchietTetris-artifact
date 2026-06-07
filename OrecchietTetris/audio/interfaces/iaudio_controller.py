from __future__ import annotations

from abc import ABC, abstractmethod


class IAudioController(ABC):
    """Contract for background-music management."""

    @abstractmethod
    def play(self) -> None:
        """Start (or resume) background music."""

    @abstractmethod
    def stop(self) -> None:
        """Stop background music."""

    @abstractmethod
    def toggle(self) -> None:
        """Toggle between playing and stopped."""

    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set volume in [0.0, 1.0]."""

    @property
    @abstractmethod
    def volume(self) -> float:
        """Current volume in [0.0, 1.0]."""

    @property
    @abstractmethod
    def is_playing(self) -> bool:
        """True while background music is playing."""

    @abstractmethod
    def next_track(self) -> None:
        """Skip to the next track in the playlist."""

    @abstractmethod
    def prev_track(self) -> None:
        """Go back to the previous track in the playlist."""
