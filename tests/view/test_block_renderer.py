import pytest
from OrecchietTetris.view.block_renderer import BlockRenderer, BLOCK_IMAGES, EMPTY_COLOUR


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
