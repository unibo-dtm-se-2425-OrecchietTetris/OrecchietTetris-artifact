import sys
from unittest.mock import MagicMock, patch

import pytest

from OrecchietTetris.view.block_renderer import (
    BlockRenderer,
    BLOCK_IMAGES,
    EMPTY_COLOUR,
    SHADOW_COLOUR,
)


def test_block_images_covers_all_piece_types():
    assert set(BLOCK_IMAGES.keys()) == {1, 2, 3, 4, 5, 6, 7}


def test_block_images_have_webp_extension():
    for val, path in BLOCK_IMAGES.items():
        assert path.endswith(".webp"), f"Expected .webp for value {val}, got {path}"


def test_empty_colour_is_valid_rgba():
    assert len(EMPTY_COLOUR) == 4
    for component in EMPTY_COLOUR:
        assert 0.0 <= component <= 1.0, "Component out of [0,1] range"


@pytest.mark.parametrize("cell_value", range(8))
def test_renderer_colour_returns_empty_colour_for_all_values(cell_value):
    renderer = BlockRenderer()
    assert renderer.colour(cell_value) == EMPTY_COLOUR


def test_renderer_colour_empty_cell_is_dark():
    r, g, b, _ = EMPTY_COLOUR
    assert r < 0.2 and g < 0.2 and b < 0.2


def test_renderer_image_path_returns_none_for_empty():
    renderer = BlockRenderer()
    assert renderer.image_path(0) is None


@pytest.mark.parametrize("cell_value", range(1, 8))
def test_renderer_image_path_returns_string_for_pieces(cell_value):
    renderer = BlockRenderer()
    path = renderer.image_path(cell_value)
    assert isinstance(path, str)
    assert len(path) > 0


def test_renderer_unknown_value_returns_empty_colour():
    renderer = BlockRenderer()
    assert renderer.colour(99) == EMPTY_COLOUR


# ---------------------------------------------------------------------------
# shadow_colour — line 60
# ---------------------------------------------------------------------------

def test_shadow_colour_returns_shadow_colour_constant() -> None:
    """shadow_colour() must return the ghost-piece tint used for the board shadow."""
    renderer = BlockRenderer()
    assert renderer.shadow_colour() == SHADOW_COLOUR


def test_shadow_colour_is_valid_rgba() -> None:
    for component in SHADOW_COLOUR:
        assert 0.0 <= component <= 1.0


# ---------------------------------------------------------------------------
# texture — line 52
# ---------------------------------------------------------------------------

def test_texture_returns_none_when_textures_not_preloaded() -> None:
    """Without calling preload_textures(), texture() must return None for all values."""
    renderer = BlockRenderer()
    for val in range(1, 8):
        assert renderer.texture(val) is None


def test_texture_returns_value_after_manual_population() -> None:
    """texture() returns whatever was stored in _textures, simulating a loaded texture."""
    renderer = BlockRenderer()
    fake_texture = MagicMock()
    renderer._textures[3] = fake_texture
    assert renderer.texture(3) is fake_texture
    assert renderer.texture(1) is None  # other keys still absent


# ---------------------------------------------------------------------------
# preload_textures — lines 40-48
# ---------------------------------------------------------------------------

def test_preload_textures_early_return_when_already_loaded() -> None:
    """preload_textures() must be idempotent — a second call must not reload."""
    renderer = BlockRenderer()
    sentinel = MagicMock()
    renderer._textures[1] = sentinel  # simulate already loaded
    renderer.preload_textures()
    # The sentinel must still be there unchanged
    assert renderer._textures[1] is sentinel
    assert len(renderer._textures) == 1  # nothing was added


def test_preload_textures_loads_images_via_kivy() -> None:
    """preload_textures() must attempt to load each block image when textures are absent."""
    renderer = BlockRenderer()
    mock_texture = MagicMock()
    mock_image = MagicMock()
    mock_image.texture = mock_texture
    mock_core_image_cls = MagicMock(return_value=mock_image)

    mock_audio_mod = MagicMock()
    mock_audio_mod.Image = mock_core_image_cls

    with patch.dict(
        sys.modules,
        {"kivy.core.image": mock_audio_mod},
    ), patch("pathlib.Path.exists", return_value=True):
        renderer.preload_textures()

    # One texture entry per piece type (1-7)
    assert len(renderer._textures) == 7
    for val in range(1, 8):
        assert renderer._textures[val] is mock_texture
