from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.audio.kivy_audio_controller import KivyAudioController
from OrecchietTetris.audio.interfaces import IAudioController


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

@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    """Reset the singleton between tests so each test gets a fresh instance."""
    KivyAudioController._instance = None
    yield
    KivyAudioController._instance = None


@pytest.fixture
def silent_controller(tmp_path: Path) -> KivyAudioController:
    """Controller pointing at an empty dir — all sound operations are no-ops."""
    empty = tmp_path / "empty"
    empty.mkdir()
    return KivyAudioController(music_path=empty)


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
def controller_with_sound(music_dir: Path, sound_mock: MagicMock) -> KivyAudioController:
    """Controller backed by a mock Kivy Sound object."""
    with _mock_sound_loader(sound_mock):
        return KivyAudioController(music_path=music_dir)


# ---------------------------------------------------------------------------
# Interface contract
# ---------------------------------------------------------------------------

def test_implements_interface(silent_controller: KivyAudioController) -> None:
    assert isinstance(silent_controller, IAudioController)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

def test_singleton_returns_same_instance() -> None:
    a = KivyAudioController()
    b = KivyAudioController()
    assert a is b


def test_singleton_not_reinitialised_on_second_call(tmp_path: Path, sound_mock: MagicMock) -> None:
    """Second instantiation with a different dir must be ignored."""
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    (dir1 / "track1.ogg").touch()

    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    (dir2 / "track2.ogg").touch()

    with _mock_sound_loader(sound_mock) as mock_audio_mod:
        first = KivyAudioController(music_path=dir1)
        second = KivyAudioController(music_path=dir2)

    assert first is second
    assert mock_audio_mod.SoundLoader.load.call_count == 1


# ---------------------------------------------------------------------------
# No-audio (silent) behaviour
# ---------------------------------------------------------------------------

def test_default_volume(silent_controller: KivyAudioController) -> None:
    assert silent_controller.volume == 0.5


def test_is_playing_false_without_sound(silent_controller: KivyAudioController) -> None:
    assert silent_controller.is_playing is False


def test_play_noop_without_sound(silent_controller: KivyAudioController) -> None:
    silent_controller.play()
    assert silent_controller.is_playing is False


def test_stop_noop_without_sound(silent_controller: KivyAudioController) -> None:
    silent_controller.stop()  # must not raise


def test_toggle_noop_without_sound(silent_controller: KivyAudioController) -> None:
    silent_controller.toggle()
    assert silent_controller.is_playing is False


def test_set_volume_updates_internal_state_without_sound(silent_controller: KivyAudioController) -> None:
    silent_controller.set_volume(0.8)
    assert silent_controller.volume == pytest.approx(0.8)


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
def test_set_volume_clamping(silent_controller: KivyAudioController,
                             input_vol: float, expected: float) -> None:
    silent_controller.set_volume(input_vol)
    assert silent_controller.volume == pytest.approx(expected)


# ---------------------------------------------------------------------------
# With mocked Kivy sound
# ---------------------------------------------------------------------------

def test_sound_initialised_with_volume(music_dir: Path, sound_mock: MagicMock) -> None:
    with _mock_sound_loader(sound_mock):
        ctrl = KivyAudioController(music_path=music_dir)

    assert sound_mock.volume == pytest.approx(ctrl.volume)
    sound_mock.bind.assert_called_once_with(on_stop=ctrl._on_track_end)


def test_play_calls_sound_play(controller_with_sound: KivyAudioController,
                               sound_mock: MagicMock) -> None:
    sound_mock.state = "stop"
    controller_with_sound.play()
    sound_mock.play.assert_called_once()


def test_play_does_not_restart_when_already_active(controller_with_sound: KivyAudioController,
                                                   sound_mock: MagicMock) -> None:
    controller_with_sound._active = True
    controller_with_sound.play()
    sound_mock.play.assert_not_called()


def test_play_does_not_call_sound_play_if_already_playing(
        controller_with_sound: KivyAudioController,
        sound_mock: MagicMock) -> None:
    sound_mock.state = "play"
    controller_with_sound._active = False
    controller_with_sound.play()
    sound_mock.play.assert_not_called()


def test_stop_mutes_all_sounds(controller_with_sound: KivyAudioController,
                               sound_mock: MagicMock) -> None:
    controller_with_sound._active = True
    controller_with_sound.stop()
    assert sound_mock.volume == pytest.approx(0.0)
    assert controller_with_sound.volume == pytest.approx(0.0)


def test_stop_does_not_call_sound_stop(controller_with_sound: KivyAudioController,
                                       sound_mock: MagicMock) -> None:
    controller_with_sound._active = True
    controller_with_sound.stop()
    sound_mock.stop.assert_not_called()


def test_stop_saves_volume(controller_with_sound: KivyAudioController) -> None:
    controller_with_sound.set_volume(0.7)
    controller_with_sound._active = True
    controller_with_sound.stop()
    assert controller_with_sound._saved_volume == pytest.approx(0.7)


def test_stop_noop_when_already_stopped(controller_with_sound: KivyAudioController,
                                        sound_mock: MagicMock) -> None:
    controller_with_sound._active = False
    controller_with_sound.set_volume(0.6)
    controller_with_sound.stop()
    assert sound_mock.volume == pytest.approx(0.6)  # unchanged


def test_play_restores_volume_after_stop(controller_with_sound: KivyAudioController,
                                         sound_mock: MagicMock) -> None:
    controller_with_sound.set_volume(0.8)
    controller_with_sound._active = True
    controller_with_sound.stop()
    assert sound_mock.volume == pytest.approx(0.0)

    sound_mock.state = "stop"
    controller_with_sound.play()
    assert sound_mock.volume == pytest.approx(0.8)
    assert controller_with_sound.volume == pytest.approx(0.8)


def test_toggle_plays_when_stopped(controller_with_sound: KivyAudioController,
                                   sound_mock: MagicMock) -> None:
    sound_mock.state = "stop"
    controller_with_sound.toggle()
    sound_mock.play.assert_called_once()


def test_toggle_mutes_when_active(controller_with_sound: KivyAudioController,
                                  sound_mock: MagicMock) -> None:
    controller_with_sound._active = True
    controller_with_sound.toggle()
    assert sound_mock.volume == pytest.approx(0.0)
    sound_mock.stop.assert_not_called()


def test_set_volume_updates_sound_volume(
        controller_with_sound: KivyAudioController,
        sound_mock: MagicMock) -> None:
    controller_with_sound.set_volume(0.3)
    assert sound_mock.volume == pytest.approx(0.3)


def test_set_volume_updates_saved_volume(
        controller_with_sound: KivyAudioController) -> None:
    controller_with_sound.set_volume(0.3)
    assert controller_with_sound._saved_volume == pytest.approx(0.3)


def test_is_playing_reflects_active_flag(
        controller_with_sound: KivyAudioController) -> None:
    assert controller_with_sound.is_playing is False
    controller_with_sound._active = True
    assert controller_with_sound.is_playing is True


def test_missing_audio_dir_gives_silent_controller(tmp_path: Path) -> None:
    missing_dir = tmp_path / "nonexistent"
    ctrl = KivyAudioController(music_path=missing_dir)
    assert ctrl.is_playing is False
    ctrl.play()
    ctrl.toggle()
    assert ctrl.volume == 0.5


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
        ctrl = KivyAudioController(music_path=d)

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
        ctrl = KivyAudioController(music_path=d)

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
        ctrl = KivyAudioController(music_path=d)

    ctrl._active = False
    ctrl._on_track_end()

    assert ctrl._idx == 0
    sounds[1].play.assert_not_called()
