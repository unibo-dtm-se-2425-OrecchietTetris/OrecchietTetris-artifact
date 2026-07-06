from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.audio.kivy_audio_service import KivyAudioService
from OrecchietTetris.audio.interfaces import IAudioService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sound(state: str = "stop") -> MagicMock:
    sound = MagicMock()
    sound.state = state
    sound.volume = 1.0
    return sound


@contextmanager
def _mock_sound_loader(sound: MagicMock) -> Generator[MagicMock, None, None]:
    """Inject a fake kivy.core.audio module so SoundLoader.load returns *sound*."""
    mock_audio_mod = MagicMock()
    mock_audio_mod.SoundLoader.load.return_value = sound
    modules = {
        "kivy": MagicMock(),
        "kivy.core": MagicMock(),
        "kivy.core.audio": mock_audio_mod,
    }
    with patch.dict(sys.modules, modules):
        yield mock_audio_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def silent_service(tmp_path: Path) -> KivyAudioService:
    """Service pointing at an empty dir — all sound operations are no-ops."""
    empty = tmp_path / "empty"
    empty.mkdir()
    return KivyAudioService(music_path=empty)


@pytest.fixture
def sound_mock() -> MagicMock:
    return _make_sound()


@pytest.fixture
def music_dir(tmp_path: Path) -> Path:
    d = tmp_path / "music"
    d.mkdir()
    (d / "track1.ogg").touch()
    return d


@pytest.fixture
def service_with_sound(music_dir: Path, sound_mock: MagicMock) -> KivyAudioService:
    """Service backed by a mock Kivy Sound object."""
    with _mock_sound_loader(sound_mock):
        return KivyAudioService(music_path=music_dir)


# ---------------------------------------------------------------------------
# Interface contract
# ---------------------------------------------------------------------------

def test_implements_interface(silent_service: KivyAudioService) -> None:
    assert isinstance(silent_service, IAudioService)


# ---------------------------------------------------------------------------
# Independent instances (dependency injection, no singleton)
# ---------------------------------------------------------------------------

def test_each_construction_returns_distinct_instance(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    a = KivyAudioService(music_path=empty)
    b = KivyAudioService(music_path=empty)
    assert a is not b


def test_each_instance_uses_its_own_music_path(tmp_path: Path, sound_mock: MagicMock) -> None:
    """Each instance loads its own directory — the path arg is always honored."""
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    (dir1 / "track1.ogg").touch()

    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    (dir2 / "track2.ogg").touch()

    with _mock_sound_loader(sound_mock) as mock_audio_mod:
        first = KivyAudioService(music_path=dir1)
        second = KivyAudioService(music_path=dir2)

    assert first is not second
    assert mock_audio_mod.SoundLoader.load.call_count == 2


# ---------------------------------------------------------------------------
# No-audio (silent) behaviour
# ---------------------------------------------------------------------------

def test_default_volume(silent_service: KivyAudioService) -> None:
    assert silent_service.volume == 0.5


def test_is_playing_false_without_sound(silent_service: KivyAudioService) -> None:
    assert silent_service.is_playing is False


def test_play_noop_without_sound(silent_service: KivyAudioService) -> None:
    silent_service.play()
    assert silent_service.is_playing is False


def test_stop_noop_without_sound(silent_service: KivyAudioService) -> None:
    silent_service.stop()  # must not raise


def test_toggle_noop_without_sound(silent_service: KivyAudioService) -> None:
    silent_service.toggle()
    assert silent_service.is_playing is False


def test_set_volume_updates_internal_state_without_sound(silent_service: KivyAudioService) -> None:
    silent_service.set_volume(0.8)
    assert silent_service.volume == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# Volume clamping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("input_vol, expected", [
    (0.0, 0.0),
    (1.0, 1.0),
    (0.5, 0.5),
    (-0.1, 0.0),
    (1.5, 1.0),
])
def test_set_volume_clamping(silent_service: KivyAudioService,
                             input_vol: float, expected: float) -> None:
    silent_service.set_volume(input_vol)
    assert silent_service.volume == pytest.approx(expected)


# ---------------------------------------------------------------------------
# With mocked Kivy sound
# ---------------------------------------------------------------------------

def test_sound_initialised_with_volume(music_dir: Path, sound_mock: MagicMock) -> None:
    with _mock_sound_loader(sound_mock):
        ctrl = KivyAudioService(music_path=music_dir)

    assert sound_mock.volume == pytest.approx(ctrl.volume)
    sound_mock.bind.assert_called_once_with(on_stop=ctrl._on_track_end)


def test_play_calls_sound_play(service_with_sound: KivyAudioService,
                               sound_mock: MagicMock) -> None:
    sound_mock.state = "stop"
    service_with_sound.play()
    sound_mock.play.assert_called_once()


def test_play_does_not_restart_when_already_active(service_with_sound: KivyAudioService,
                                                   sound_mock: MagicMock) -> None:
    service_with_sound._active = True
    service_with_sound.play()
    sound_mock.play.assert_not_called()


def test_play_does_not_call_sound_play_if_already_playing(
        service_with_sound: KivyAudioService,
        sound_mock: MagicMock) -> None:
    sound_mock.state = "play"
    service_with_sound._active = False
    service_with_sound.play()
    sound_mock.play.assert_not_called()


def test_stop_mutes_all_sounds(service_with_sound: KivyAudioService,
                               sound_mock: MagicMock) -> None:
    service_with_sound._active = True
    service_with_sound.stop()
    assert sound_mock.volume == pytest.approx(0.0)
    assert service_with_sound.volume == pytest.approx(0.0)


def test_stop_does_not_call_sound_stop(service_with_sound: KivyAudioService,
                                       sound_mock: MagicMock) -> None:
    service_with_sound._active = True
    service_with_sound.stop()
    sound_mock.stop.assert_not_called()


def test_stop_saves_volume(service_with_sound: KivyAudioService) -> None:
    service_with_sound.set_volume(0.7)
    service_with_sound._active = True
    service_with_sound.stop()
    assert service_with_sound._saved_volume == pytest.approx(0.7)


def test_stop_noop_when_already_stopped(service_with_sound: KivyAudioService,
                                        sound_mock: MagicMock) -> None:
    service_with_sound._active = False
    service_with_sound.set_volume(0.6)
    service_with_sound.stop()
    assert sound_mock.volume == pytest.approx(0.6)  # unchanged


def test_play_restores_volume_after_stop(service_with_sound: KivyAudioService,
                                         sound_mock: MagicMock) -> None:
    service_with_sound.set_volume(0.8)
    service_with_sound._active = True
    service_with_sound.stop()
    assert sound_mock.volume == pytest.approx(0.0)

    sound_mock.state = "stop"
    service_with_sound.play()
    assert sound_mock.volume == pytest.approx(0.8)
    assert service_with_sound.volume == pytest.approx(0.8)


def test_toggle_plays_when_stopped(service_with_sound: KivyAudioService,
                                   sound_mock: MagicMock) -> None:
    sound_mock.state = "stop"
    service_with_sound.toggle()
    sound_mock.play.assert_called_once()


def test_toggle_mutes_when_active(service_with_sound: KivyAudioService,
                                  sound_mock: MagicMock) -> None:
    service_with_sound._active = True
    service_with_sound.toggle()
    assert sound_mock.volume == pytest.approx(0.0)
    sound_mock.stop.assert_not_called()


def test_set_volume_updates_sound_volume(
        service_with_sound: KivyAudioService,
        sound_mock: MagicMock) -> None:
    service_with_sound.set_volume(0.3)
    assert sound_mock.volume == pytest.approx(0.3)


def test_set_volume_updates_saved_volume(
        service_with_sound: KivyAudioService) -> None:
    service_with_sound.set_volume(0.3)
    assert service_with_sound._saved_volume == pytest.approx(0.3)


def test_is_playing_reflects_active_flag(
        service_with_sound: KivyAudioService) -> None:
    assert service_with_sound.is_playing is False
    service_with_sound._active = True
    assert service_with_sound.is_playing is True


def test_missing_audio_dir_gives_silent_service(tmp_path: Path) -> None:
    missing_dir = tmp_path / "nonexistent"
    ctrl = KivyAudioService(music_path=missing_dir)
    assert ctrl.is_playing is False
    ctrl.play()
    ctrl.toggle()
    assert ctrl.volume == 0.5


def test_load_queue_skips_non_audio_files(tmp_path: Path, sound_mock: MagicMock) -> None:
    """Files whose extension is not in _EXTENSIONS are skipped."""
    d = tmp_path / "music"
    d.mkdir()
    (d / "track.ogg").touch()
    (d / "notes.txt").touch()  # must be ignored

    with _mock_sound_loader(sound_mock) as mock_audio_mod:
        ctrl = KivyAudioService(music_path=d)

    assert len(ctrl._queue) == 1
    mock_audio_mod.SoundLoader.load.assert_called_once()


# ---------------------------------------------------------------------------
# Queue auto-advance
# ---------------------------------------------------------------------------

def test_queue_advances_on_track_end(tmp_path: Path) -> None:
    """_on_track_end advances idx and plays next track."""
    d = tmp_path / "music"
    d.mkdir()
    (d / "a.ogg").touch()
    (d / "b.ogg").touch()

    sound_a = _make_sound()
    sound_b = _make_sound()
    sounds = [sound_a, sound_b]
    load_idx = 0

    mock_audio_mod = MagicMock()

    def load_side_effect(_: str) -> MagicMock:
        nonlocal load_idx
        s = sounds[load_idx % len(sounds)]
        load_idx += 1
        return s

    mock_audio_mod.SoundLoader.load.side_effect = load_side_effect
    modules = {"kivy": MagicMock(), "kivy.core": MagicMock(), "kivy.core.audio": mock_audio_mod}

    with patch.dict(sys.modules, modules):
        ctrl = KivyAudioService(music_path=d)

    ctrl._active = True
    ctrl._on_track_end()

    assert ctrl._idx == 1
    sound_b.play.assert_called_once()


def test_queue_wraps_around(tmp_path: Path) -> None:
    """After last track ends, queue wraps to index 0."""
    d = tmp_path / "music"
    d.mkdir()
    (d / "a.ogg").touch()

    sound_a = _make_sound()
    mock_audio_mod = MagicMock()
    mock_audio_mod.SoundLoader.load.return_value = sound_a
    modules = {"kivy": MagicMock(), "kivy.core": MagicMock(), "kivy.core.audio": mock_audio_mod}

    with patch.dict(sys.modules, modules):
        ctrl = KivyAudioService(music_path=d)

    ctrl._active = True
    ctrl._on_track_end()

    assert ctrl._idx == 0
    sound_a.play.assert_called_once()


def test_queue_does_not_advance_when_inactive(tmp_path: Path) -> None:
    """_on_track_end is a no-op when _active=False."""
    d = tmp_path / "music"
    d.mkdir()
    (d / "a.ogg").touch()
    (d / "b.ogg").touch()

    sounds = [_make_sound(), _make_sound()]
    load_idx = 0
    mock_audio_mod = MagicMock()

    def load_side_effect(_: str) -> MagicMock:
        nonlocal load_idx
        s = sounds[load_idx % len(sounds)]
        load_idx += 1
        return s

    mock_audio_mod.SoundLoader.load.side_effect = load_side_effect
    modules = {"kivy": MagicMock(), "kivy.core": MagicMock(), "kivy.core.audio": mock_audio_mod}

    with patch.dict(sys.modules, modules):
        ctrl = KivyAudioService(music_path=d)

    ctrl._active = False
    ctrl._on_track_end()

    assert ctrl._idx == 0
    sounds[1].play.assert_not_called()


# ---------------------------------------------------------------------------
# next_track / prev_track
# ---------------------------------------------------------------------------

def _make_two_track_service(tmp_path: Path) -> tuple[KivyAudioService, MagicMock, MagicMock]:
    d = tmp_path / "music"
    d.mkdir()
    (d / "a.ogg").touch()
    (d / "b.ogg").touch()

    sound_a = _make_sound()
    sound_b = _make_sound()
    sounds = [sound_a, sound_b]
    load_idx = 0
    mock_audio_mod = MagicMock()

    def load_side_effect(_: str) -> MagicMock:
        nonlocal load_idx
        s = sounds[load_idx % len(sounds)]
        load_idx += 1
        return s

    mock_audio_mod.SoundLoader.load.side_effect = load_side_effect
    modules = {"kivy": MagicMock(), "kivy.core": MagicMock(), "kivy.core.audio": mock_audio_mod}

    with patch.dict(sys.modules, modules):
        ctrl = KivyAudioService(music_path=d)

    return ctrl, sound_a, sound_b


def test_next_track_noop_without_sound(silent_service: KivyAudioService) -> None:
    silent_service.next_track()  # must not raise


def test_prev_track_noop_without_sound(silent_service: KivyAudioService) -> None:
    silent_service.prev_track()  # must not raise


def test_next_track_advances_and_plays_when_active(tmp_path: Path) -> None:
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = True
    ctrl.next_track()

    assert ctrl._idx == 1
    sound_a.stop.assert_called_once()
    sound_b.play.assert_called_once()


def test_next_track_wraps_to_first_from_last(tmp_path: Path) -> None:
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = True
    ctrl._idx = 1
    ctrl.next_track()

    assert ctrl._idx == 0
    sound_b.stop.assert_called_once()
    sound_a.play.assert_called_once()


def test_next_track_noop_when_inactive(tmp_path: Path) -> None:
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = False
    ctrl.next_track()

    assert ctrl._idx == 0
    sound_a.stop.assert_not_called()
    sound_b.play.assert_not_called()


def test_prev_track_goes_back_and_plays_when_active(tmp_path: Path) -> None:
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = True
    ctrl._idx = 1
    ctrl.prev_track()

    assert ctrl._idx == 0
    sound_b.stop.assert_called_once()
    sound_a.play.assert_called_once()


def test_prev_track_wraps_to_last_from_first(tmp_path: Path) -> None:
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = True
    ctrl._idx = 0
    ctrl.prev_track()

    assert ctrl._idx == 1
    sound_a.stop.assert_called_once()
    sound_b.play.assert_called_once()


def test_prev_track_noop_when_inactive(tmp_path: Path) -> None:
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = False
    ctrl.prev_track()

    assert ctrl._idx == 0
    sound_a.stop.assert_not_called()
    sound_b.play.assert_not_called()


def test_next_track_does_not_double_advance_when_stop_fires_on_track_end(tmp_path: Path) -> None:
    """Regression: stop() fires on_stop -> _on_track_end, which must not advance idx again."""
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = True

    def stop_side_effect() -> None:
        ctrl._on_track_end()

    sound_a.stop.side_effect = stop_side_effect
    ctrl.next_track()

    assert ctrl._idx == 1
    sound_b.play.call_count == 1


def test_prev_track_does_not_double_advance_when_stop_fires_on_track_end(tmp_path: Path) -> None:
    """Regression: same as above for prev_track."""
    ctrl, sound_a, sound_b = _make_two_track_service(tmp_path)
    ctrl._active = True
    ctrl._idx = 1

    def stop_side_effect() -> None:
        ctrl._on_track_end()

    sound_b.stop.side_effect = stop_side_effect
    ctrl.prev_track()

    assert ctrl._idx == 0
    sound_a.play.call_count == 1


# ---------------------------------------------------------------------------
# _load_queue: exception path — lines 126-127
# ---------------------------------------------------------------------------

def test_load_queue_returns_empty_when_kivy_audio_import_raises(tmp_path: Path) -> None:
    """_load_queue() must silently return [] when importing kivy.core.audio
    raises any Exception (not only ImportError), covering the broad except
    clause that keeps the service usable even in broken environments.
    """
    audio_dir = tmp_path / "music"
    audio_dir.mkdir()
    (audio_dir / "track.ogg").touch()

    with patch.dict(
        sys.modules,
        {
            "kivy": MagicMock(),
            "kivy.core": MagicMock(),
            "kivy.core.audio": None,  # None in sys.modules raises ImportError on import
        },
    ):
        result = KivyAudioService._load_queue(audio_dir)

    assert result == []
