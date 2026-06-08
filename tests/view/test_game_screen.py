from __future__ import annotations

import os
from typing import Any

from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.view.game_screen import GAME_SCREEN_BG, _cover_tex_coords
from OrecchietTetris.utils import EventType


def test_game_screen_bg_constant_ends_with_webp():
    assert GAME_SCREEN_BG.endswith(".webp")


def test_game_screen_bg_file_exists():
    assert os.path.exists(GAME_SCREEN_BG), f"Background image missing: {GAME_SCREEN_BG}"


def test_cover_tex_coords_identity():
    # v is flipped: bottom of rect maps to v=1 (bottom of image), top to v=0
    coords = _cover_tex_coords(100.0, 100.0, 100.0, 100.0)
    assert coords == (0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)


def test_cover_tex_coords_wide_image_crops_sides():
    # 2:1 image in a 1:1 window — horizontal crop, centre; v stays flipped
    coords = _cover_tex_coords(200.0, 100.0, 100.0, 100.0)
    u0, v_bottom, u1, _, _, v_top, _, _ = coords
    assert abs(u0 - 0.25) < 1e-9
    assert abs(u1 - 0.75) < 1e-9
    assert v_bottom == 1.0 and v_top == 0.0


def test_cover_tex_coords_tall_image_crops_top_bottom():
    # 1:2 image in a 1:1 window — vertical crop, centre; v stays flipped
    coords = _cover_tex_coords(100.0, 200.0, 100.0, 100.0)
    u0, v_bottom, u1, _, _, v_top, _, _ = coords
    assert u0 == 0.0 and u1 == 1.0
    # shown_h=0.5 → v0=0.25, v1=0.75; bottom maps to v1, top to v0
    assert abs(v_bottom - 0.75) < 1e-9
    assert abs(v_top - 0.25) < 1e-9


def test_cover_tex_coords_zero_height_returns_default():
    coords = _cover_tex_coords(100.0, 0.0, 100.0, 100.0)
    assert coords == (0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)


def test_cover_tex_coords_zero_win_height_returns_default():
    coords = _cover_tex_coords(100.0, 100.0, 100.0, 0.0)
    assert coords == (0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# GameScreen instantiation and IView
# ---------------------------------------------------------------------------

def _make_model() -> MagicMock:
    model = MagicMock()
    model.is_game_over = False
    model.is_paused = False
    model.is_running = True
    model.score = 0
    model.level = 1
    model.lines_cleared = 0
    model.shadow_row = 0
    model.current_piece = None
    model.current_col = 0
    model.next_piece = None
    model.held_piece = None
    model.can_hold = True
    model.board.grid = [[0] * 10 for _ in range(20)]
    return model


@pytest.fixture()
def model() -> MagicMock:
    return _make_model()


@pytest.fixture()
def audio() -> MagicMock:
    mock = MagicMock()
    mock.is_playing = True
    return mock


@pytest.fixture()
def repo() -> MagicMock:
    return MagicMock()


def _make_game_screen(*args, **kwargs):
    from OrecchietTetris.view.game_screen import GameScreen
    with (
        patch("OrecchietTetris.view.block_renderer.BlockRenderer.preload_textures"),
        patch("OrecchietTetris.view.game_screen.GameScreen._load_bg_image"),
    ):
        return GameScreen(*args, **kwargs)


@pytest.fixture()
def gs(model: MagicMock) -> Any:
    return _make_game_screen(model=model, name="game")


@pytest.fixture()
def gs_with_audio(model: MagicMock, audio: MagicMock, repo: MagicMock) -> Any:
    return _make_game_screen(
        model=model,
        audio=audio,
        repository=repo,
        on_back_to_menu=MagicMock(),
        on_name_saved=MagicMock(),
        name="game",
    )


def test_game_screen_can_be_instantiated(gs) -> None:
    assert gs is not None


def test_game_screen_with_audio_can_be_instantiated(gs_with_audio) -> None:
    assert gs_with_audio is not None


def test_show_makes_screen_visible_and_attaches_observer(gs, model) -> None:
    gs.show()
    assert gs.opacity == 1.0
    assert gs.disabled is False
    model.attach.assert_called_once_with(gs)


def test_hide_makes_screen_invisible_and_detaches_observer(gs, model) -> None:
    gs.show()
    gs.hide()
    assert gs.opacity == 0.0
    assert gs.disabled is True
    model.detach.assert_called_once_with(gs)


# ---------------------------------------------------------------------------
# update — EventType dispatch
# ---------------------------------------------------------------------------

def test_update_lines_cleared_sets_animating_flag(gs) -> None:
    with patch("OrecchietTetris.view.game_screen.Clock"):
        gs.update(EventType.LINES_CLEARED, ([], []))
    assert gs._board.is_animating is True


def test_update_schedules_dispatch_on_clock(gs) -> None:
    with patch("OrecchietTetris.view.game_screen.Clock") as mock_clock:
        gs.update(EventType.SCORE_UPDATED, None)
        mock_clock.schedule_once.assert_called_once()


# ---------------------------------------------------------------------------
# _dispatch — each EventType branch
# ---------------------------------------------------------------------------

def _dispatch_sync(gs, event_type: EventType, data) -> None:
    """Call _dispatch directly (bypasses Clock.schedule_once)."""
    gs._dispatch(event_type, data)


def test_dispatch_board_updated_calls_redraw_when_not_animating(gs) -> None:
    gs._board.is_animating = False
    gs._board.redraw = MagicMock()
    _dispatch_sync(gs, EventType.BOARD_UPDATED, None)
    gs._board.redraw.assert_called_once()


def test_dispatch_board_updated_skips_redraw_when_animating(gs) -> None:
    gs._board.is_animating = True
    gs._board.redraw = MagicMock()
    _dispatch_sync(gs, EventType.BOARD_UPDATED, None)
    gs._board.redraw.assert_not_called()


def test_dispatch_new_piece_updates_next_preview(gs, model) -> None:
    gs._board.is_animating = False
    gs._next_preview.set_piece = MagicMock()
    _dispatch_sync(gs, EventType.NEW_PIECE, None)
    gs._next_preview.set_piece.assert_called_once()


def test_dispatch_score_updated_updates_labels(gs, model) -> None:
    model.score = 1234
    model.level = 3
    _dispatch_sync(gs, EventType.SCORE_UPDATED, None)
    assert gs._lbl_score.text == "1234"
    assert gs._lbl_level.text == "3"


def test_dispatch_lines_cleared_starts_animation(gs, model) -> None:
    model.lines_cleared = 4
    model.board.grid = [[0] * 10 for _ in range(20)]
    model.shadow_row = 0
    model.current_piece = None
    model.current_col = 0

    with patch.object(gs._board, "animate_line_clear") as mock_anim:
        _dispatch_sync(gs, EventType.LINES_CLEARED, ({3, 7}, [[0] * 10 for _ in range(20)]))
    mock_anim.assert_called_once()


def test_dispatch_game_over_shows_overlay(gs) -> None:
    _dispatch_sync(gs, EventType.GAME_OVER, None)
    assert gs._overlay is not None


def test_dispatch_paused_changes_pause_button(gs) -> None:
    _dispatch_sync(gs, EventType.PAUSED, None)
    assert gs._btn_pause.text == ""


def test_dispatch_resumed_changes_pause_button(gs) -> None:
    _dispatch_sync(gs, EventType.RESUMED, None)
    assert gs._btn_pause.text == ""


def test_dispatch_hold_updated_refreshes_hold_preview(gs, model) -> None:
    model.held_piece = None
    model.can_hold = True
    gs._hold_preview.set_piece = MagicMock()
    _dispatch_sync(gs, EventType.HOLD_UPDATED, None)
    gs._hold_preview.set_piece.assert_called_once()


# ---------------------------------------------------------------------------
# _on_key_down
# ---------------------------------------------------------------------------

def _key_down(gs, key: str) -> bool:
    return gs._on_key_down(None, (0, key), "", [])  # type: ignore[no-any-return]


def test_key_left_calls_move_left(gs, model) -> None:
    _key_down(gs, "left")
    model.move_left.assert_called_once()


def test_key_right_calls_move_right(gs, model) -> None:
    _key_down(gs, "right")
    model.move_right.assert_called_once()


def test_key_down_calls_move_down(gs, model) -> None:
    _key_down(gs, "down")
    model.move_down.assert_called_once()


def test_key_up_calls_rotate(gs, model) -> None:
    _key_down(gs, "up")
    model.rotate.assert_called_once()


def test_key_x_calls_rotate(gs, model) -> None:
    _key_down(gs, "x")
    model.rotate.assert_called_once()


def test_key_spacebar_calls_hard_drop(gs, model) -> None:
    _key_down(gs, "spacebar")
    model.hard_drop.assert_called_once()


def test_key_c_calls_hold(gs, model) -> None:
    _key_down(gs, "c")
    model.hold.assert_called_once()


def test_key_p_calls_handle_pause(gs) -> None:
    gs._handle_pause = MagicMock()
    _key_down(gs, "p")
    gs._handle_pause.assert_called_once()


def test_key_escape_calls_handle_pause(gs) -> None:
    gs._handle_pause = MagicMock()
    _key_down(gs, "escape")
    gs._handle_pause.assert_called_once()


def test_key_m_calls_toggle_music(gs) -> None:
    gs._toggle_music = MagicMock()
    _key_down(gs, "m")
    gs._toggle_music.assert_called_once()


def test_key_n_calls_next_track(gs_with_audio, audio) -> None:
    _key_down(gs_with_audio, "n")
    audio.next_track.assert_called_once()


def test_key_b_calls_prev_track(gs_with_audio, audio) -> None:
    _key_down(gs_with_audio, "b")
    audio.prev_track.assert_called_once()


def test_key_q_opens_quit_overlay(gs) -> None:
    with patch.object(gs, "_show_quit_confirm_overlay") as mock_show:
        _key_down(gs, "q")
        mock_show.assert_called_once()


def test_key_q_dismisses_quit_overlay_if_already_open(gs) -> None:
    gs._quit_overlay = MagicMock()
    with patch.object(gs, "_dismiss_quit_overlay") as mock_dismiss:
        _key_down(gs, "q")
        mock_dismiss.assert_called_once()


def test_key_during_countdown_returns_true_without_action(gs, model) -> None:
    gs._countdown_overlay = MagicMock()  # active countdown
    result = _key_down(gs, "left")
    model.move_left.assert_not_called()
    assert result is True


def test_key_when_game_over_returns_false(gs, model) -> None:
    model.is_game_over = True
    result = _key_down(gs, "left")
    model.move_left.assert_not_called()
    assert result is False


# ---------------------------------------------------------------------------
# Overlays
# ---------------------------------------------------------------------------

def test_show_game_over_overlay_creates_overlay(gs) -> None:
    gs._show_game_over_overlay(name_input=False)
    assert gs._overlay is not None


def test_show_game_over_overlay_idempotent(gs) -> None:
    gs._show_game_over_overlay(name_input=False)
    first_overlay = gs._overlay
    gs._show_game_over_overlay(name_input=False)
    assert gs._overlay is first_overlay  # not replaced


def test_handle_back_to_menu_clears_overlay_and_calls_callback(gs) -> None:
    on_back = MagicMock()
    gs._on_back_to_menu = on_back
    gs._show_game_over_overlay(name_input=False)
    gs._handle_back_to_menu()
    assert gs._overlay is None
    on_back.assert_called_once()


def test_handle_try_again_clears_overlay_and_calls_on_try_again(gs) -> None:
    on_try = MagicMock()
    gs._on_try_again = on_try
    gs._show_game_over_overlay(name_input=False)
    gs._handle_try_again()
    assert gs._overlay is None
    on_try.assert_called_once()


def test_show_quit_confirm_overlay_creates_overlay(gs) -> None:
    gs._show_quit_confirm_overlay()
    assert gs._quit_overlay is not None


def test_show_quit_confirm_overlay_idempotent(gs) -> None:
    gs._show_quit_confirm_overlay()
    first = gs._quit_overlay
    gs._show_quit_confirm_overlay()
    assert gs._quit_overlay is first


def test_dismiss_quit_overlay_removes_it(gs, model) -> None:
    model.is_paused = False
    gs._show_quit_confirm_overlay()
    gs._dismiss_quit_overlay()
    assert gs._quit_overlay is None


def test_dismiss_quit_overlay_resumes_if_paused(gs, model) -> None:
    model.is_paused = True
    gs._quit_overlay = MagicMock()
    gs._dismiss_quit_overlay()
    model.resume.assert_called_once()


def test_confirm_quit_calls_back_to_menu(gs, model) -> None:
    on_back = MagicMock()
    gs._on_back_to_menu = on_back
    model.is_running = True
    gs._quit_overlay = MagicMock()
    gs._confirm_quit()
    model.stop.assert_called_once()
    on_back.assert_called_once()
    assert gs._quit_overlay is None


# ---------------------------------------------------------------------------
# _handle_pause — pause and resume paths
# ---------------------------------------------------------------------------

def test_handle_pause_pauses_when_not_paused(gs, model) -> None:
    model.is_paused = False
    gs._handle_pause()
    model.pause.assert_called_once()


def test_handle_pause_shows_countdown_when_already_paused(gs, model) -> None:
    model.is_paused = True
    with patch.object(gs, "_show_countdown") as mock_countdown:
        gs._handle_pause()
        mock_countdown.assert_called_once()


# ---------------------------------------------------------------------------
# _toggle_music
# ---------------------------------------------------------------------------

def test_toggle_music_calls_audio_toggle(gs_with_audio, audio) -> None:
    gs_with_audio._toggle_music()
    audio.toggle.assert_called_once()


def test_toggle_music_without_audio_does_not_raise(gs) -> None:
    gs._toggle_music()  # no audio → must not raise


# ---------------------------------------------------------------------------
# _show_countdown / _countdown_step
# ---------------------------------------------------------------------------

def test_show_countdown_runs_callback_synchronously(gs) -> None:
    callback = MagicMock()
    with patch("OrecchietTetris.view.game_screen.Clock") as mock_clock:
        mock_clock.schedule_once.side_effect = lambda cb, delay: cb(0)
        gs._show_countdown(callback)
    callback.assert_called_once()


def test_show_countdown_is_idempotent(gs) -> None:
    """A second call while countdown is active must not create a second overlay."""
    with patch("OrecchietTetris.view.game_screen.Clock") as mock_clock:
        mock_clock.schedule_once.side_effect = lambda cb, delay: None  # don't advance
        gs._show_countdown(MagicMock())
        first_overlay = gs._countdown_overlay
        gs._show_countdown(MagicMock())
        assert gs._countdown_overlay is first_overlay


# ---------------------------------------------------------------------------
# _update_bg and _on_window_resize helpers
# ---------------------------------------------------------------------------

def test_update_bg_syncs_rects(gs) -> None:
    gs.pos = (0, 0)
    gs.size = (800, 600)
    gs._update_bg()
    assert gs._bg_fill_rect.pos == (0, 0)
    assert gs._bg_fill_rect.size == (800, 600)


def test_on_window_resize_updates_board_and_root(gs) -> None:
    with patch.object(gs._board, "resize") as mock_resize:
        gs._on_window_resize(None, 1024, 768)
        mock_resize.assert_called_once()


# ---------------------------------------------------------------------------
# _show_game_over_overlay with name input
# ---------------------------------------------------------------------------

def test_game_over_with_repo_adds_name_input(gs_with_audio, repo) -> None:
    gs_with_audio._show_game_over_overlay(name_input=True)
    assert gs_with_audio._overlay is not None


# ---------------------------------------------------------------------------
# start_with_countdown / _restart — lines 140, 143-147
# ---------------------------------------------------------------------------

def test_start_with_countdown_delegates_to_show_countdown(gs) -> None:
    gs.restart = MagicMock()  # inject the attribute start_with_countdown expects
    with patch.object(gs, "_show_countdown") as mock_cd:
        gs.start_with_countdown()
        mock_cd.assert_called_once_with(gs.restart)


def test_restart_calls_model_play_and_updates_labels(gs, model) -> None:
    model.score = 100
    model.level = 2
    model.lines_cleared = 5
    model.held_piece = None
    model.can_hold = True
    gs._restart()
    model.play.assert_called_once()
    assert gs._lbl_score.text == "100"
    assert gs._lbl_level.text == "2"
    assert gs._lbl_lines.text == "5"


# ---------------------------------------------------------------------------
# _on_keyboard_closed — line 270
# ---------------------------------------------------------------------------

def test_on_keyboard_closed_clears_keyboard_reference(gs) -> None:
    gs._keyboard = MagicMock()
    gs._on_keyboard_closed()
    assert gs._keyboard is None


# ---------------------------------------------------------------------------
# _handle_quit early return — line 425
# ---------------------------------------------------------------------------

def test_handle_quit_is_noop_when_overlay_already_open(gs, model) -> None:
    """_handle_quit must return immediately if the quit overlay is already shown."""
    gs._quit_overlay = MagicMock()
    gs._handle_quit()
    model.pause.assert_not_called()


# ---------------------------------------------------------------------------
# _load_bg_image — lines 463-470
# ---------------------------------------------------------------------------

def test_load_bg_image_sets_texture_when_file_exists(gs) -> None:
    from unittest.mock import MagicMock, patch
    mock_core_img = MagicMock()
    mock_core_img.texture = MagicMock()
    mock_core_img.texture.width = 100.0
    mock_core_img.texture.height = 100.0

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("OrecchietTetris.view.game_screen.GameScreen._update_bg"),
    ):
        import sys
        mock_image_mod = MagicMock()
        mock_image_mod.Image = MagicMock(return_value=mock_core_img)
        with patch.dict(sys.modules, {"kivy.core.image": mock_image_mod}):
            gs._bg_image_color = MagicMock()
            gs._bg_rect = MagicMock()
            gs._load_bg_image()
    assert gs._bg_core_image is not None


def test_load_bg_image_skips_when_file_missing(gs) -> None:
    with patch("pathlib.Path.exists", return_value=False):
        gs._bg_core_image = None
        gs._load_bg_image()
    assert gs._bg_core_image is None


# ---------------------------------------------------------------------------
# _update_bg with bg_core_image — lines 708-709
# ---------------------------------------------------------------------------

def test_update_bg_computes_tex_coords_when_bg_image_set(gs) -> None:
    gs._bg_core_image = MagicMock()
    gs._bg_core_image.texture.width = 800.0
    gs._bg_core_image.texture.height = 600.0
    gs.width = 800.0
    gs.height = 600.0
    gs._update_bg()
    # tex_coords must have been set on the rect
    assert gs._bg_rect.tex_coords is not None


# ---------------------------------------------------------------------------
# _on_save closure — lines 367-380
# ---------------------------------------------------------------------------

def test_on_save_closure_saves_entry_and_shows_no_name_overlay(gs_with_audio, model, repo) -> None:
    """_on_save must persist the entry, call on_name_saved, and refresh the overlay."""
    from OrecchietTetris.view.widgets.dialog_overlay import DialogOverlay

    captured_callbacks: list = []

    def capturing_add_button(self_dlg, text, bg, on_release, **kwargs):
        captured_callbacks.append(on_release)
        return MagicMock()

    with patch.object(DialogOverlay, "add_button", capturing_add_button):
        # Show the overlay with name input — this defines and binds _on_save
        gs_with_audio._overlay = None
        gs_with_audio._show_game_over_overlay(name_input=True)

    # First callback captured is the save button's on_release
    assert captured_callbacks, "Expected save callback to be captured"
    save_cb = captured_callbacks[0]

    # Simulate an existing overlay so that the 'remove_widget' branch (378-379) runs
    gs_with_audio._overlay = MagicMock()

    save_cb()  # triggers lines 367-380

    repo.save.assert_called_once()
    gs_with_audio._on_name_saved.assert_called_once()
