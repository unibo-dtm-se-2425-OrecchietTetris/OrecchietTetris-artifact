from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Optional

from OrecchietTetris.audio.interfaces.iaudio_controller import IAudioController
from OrecchietTetris.utils.paths import MUSIC_DIR

_EXTENSIONS = {".ogg", ".mp3", ".wav"}


class KivyAudioController(IAudioController):
    """Singleton audio controller backed by Kivy's SoundLoader.

    Discovers all audio files in MUSIC_DIR and plays them as a looping queue.
    stop() mutes playback and saves volume; play() restores it.
    Gracefully handles missing/unloadable files — all methods become no-ops.
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
        self._saved_volume: float = 0.5
        self._queue: list[Any] = []
        self._idx: int = 0
        self._active: bool = False

        folder = music_path if music_path is not None else MUSIC_DIR
        self._queue = self._load_queue(folder)
        for sound in self._queue:
            sound.volume = self._volume
            sound.bind(on_stop=self._on_track_end)

        self._initialized: bool = True

    # ------------------------------------------------------------------
    # IAudioController
    # ------------------------------------------------------------------

    def play(self) -> None:
        if not self._queue or self._active:
            return
        self._active = True
        self._volume = self._saved_volume
        for sound in self._queue:
            sound.volume = self._volume
        if self._queue[self._idx].state != "play":
            self._queue[self._idx].play()

    def stop(self) -> None:
        if not self._queue or not self._active:
            return
        self._active = False
        self._saved_volume = self._volume
        self._volume = 0.0
        for sound in self._queue:
            sound.volume = 0.0

    def toggle(self) -> None:
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        self._saved_volume = self._volume
        for sound in self._queue:
            sound.volume = self._volume

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def is_playing(self) -> bool:
        return self._active and bool(self._queue)

    # ------------------------------------------------------------------
    # Queue logic
    # ------------------------------------------------------------------

    def _on_track_end(self, *_: Any) -> None:
        if not self._active or not self._queue:
            return
        self._idx = (self._idx + 1) % len(self._queue)
        self._queue[self._idx].play()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_queue(folder: Path) -> list[Any]:
        if not folder.exists():
            return []
        try:
            from kivy.core.audio import SoundLoader  # type: ignore[import-untyped]
        except Exception:
            return []
        sounds = []
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in _EXTENSIONS:
                continue
            sound = SoundLoader.load(str(path))
            if sound is not None:
                sounds.append(sound)
        return sounds
