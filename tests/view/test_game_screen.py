import os

from OrecchietTetris.view.game_screen import GAME_SCREEN_BG, _cover_tex_coords


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
