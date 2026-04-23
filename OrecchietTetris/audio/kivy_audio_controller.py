from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Optional

from OrecchietTetris.audio.interfaces.iaudio_controller import IAudioController
from OrecchietTetris.utils.paths import MUSIC_DIR

_SOUND_DIR = Path(__file__).parent.parent.parent / "assets" / "sound"
_EXTENSIONS = ("ogg", "mp3", "wav")


class KivyAudioController(IAudioController):
    """Singleton audio controller backed by Kivy's SoundLoader.

    Gracefully handles missing audio files: all methods are no-ops when no
    background track is found in ``assets/sound/background.{ogg,mp3,wav}``.
    """

    _instance: ClassVar[Optional[KivyAudioController]] = None

    def __new__(cls, music_path: Optional[Path] = None) -> KivyAudioController:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, music_path: Optional[Path] = None) -> None:
        if hasattr(self, "_initialized"):
            return
        self._volume: float = 0.5
        self._sound: Any = None
        path = music_path if music_path is not None else self._discover()
        if path is not None and path.exists():
            from kivy.core.audio import SoundLoader  # type: ignore[import-untyped]
            self._sound = SoundLoader.load(str(path))
            if self._sound is not None:
                self._sound.loop = True
                self._sound.volume = self._volume
        self._initialized: bool = True

    # ------------------------------------------------------------------
    # IAudioController
    # ------------------------------------------------------------------

    def play(self) -> None:
        if self._sound is not None and not self.is_playing:
            self._sound.play()

    def stop(self) -> None:
        if self._sound is not None and self.is_playing:
            self._sound.stop()

    def toggle(self) -> None:
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        if self._sound is not None:
            self._sound.volume = self._volume

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def is_playing(self) -> bool:
        return self._sound is not None and self._sound.state == "play"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _discover() -> Optional[Path]:
        for ext in _EXTENSIONS:
            p = MUSIC_DIR / f"background.{ext}"
            if p.exists():
                return p
        return None
