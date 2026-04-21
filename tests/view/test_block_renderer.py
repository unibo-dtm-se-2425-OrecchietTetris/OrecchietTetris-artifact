import pytest
from OrecchietTetris.view.block_renderer import BlockRenderer, BLOCK_IMAGES, BLOCK_COLOURS


def test_block_images_covers_all_piece_types():
    assert set(BLOCK_IMAGES.keys()) == {1, 2, 3, 4, 5, 6, 7}


def test_block_images_have_webp_extension():
    for val, path in BLOCK_IMAGES.items():
        assert path.endswith(".webp"), f"Expected .webp for value {val}, got {path}"


def test_block_colours_covers_empty_and_all_pieces():
    # 0 = empty, 1-7 = piece types
    assert set(BLOCK_COLOURS.keys()) == {0, 1, 2, 3, 4, 5, 6, 7}


def test_block_colours_are_valid_rgba():
    for val, rgba in BLOCK_COLOURS.items():
        assert len(rgba) == 4, f"Colour for {val} must be a 4-tuple"
        for component in rgba:
            assert 0.0 <= component <= 1.0, f"Component out of [0,1] range for value {val}"


@pytest.mark.parametrize("cell_value", range(8))
def test_renderer_colour_returns_tuple_for_all_values(cell_value):
    renderer = BlockRenderer()
    colour = renderer.colour(cell_value)
    assert isinstance(colour, tuple)
    assert len(colour) == 4


def test_renderer_colour_empty_cell_is_dark():
    renderer = BlockRenderer()
    r, g, b, a = renderer.colour(0)
    # Empty cells should be dark (all channels < 0.2)
    assert r < 0.2 and g < 0.2 and b < 0.2


def test_renderer_shadow_colour_is_semi_transparent():
    renderer = BlockRenderer()
    _, _, _, a = renderer.shadow_colour()
    assert a < 0.5, "Shadow should be semi-transparent"


def test_renderer_image_path_returns_none_for_empty():
    renderer = BlockRenderer()
    assert renderer.image_path(0) is None


@pytest.mark.parametrize("cell_value", range(1, 8))
def test_renderer_image_path_returns_string_for_pieces(cell_value):
    renderer = BlockRenderer()
    path = renderer.image_path(cell_value)
    assert isinstance(path, str)
    assert len(path) > 0


def test_renderer_unknown_value_falls_back_to_empty_colour():
    renderer = BlockRenderer()
    colour = renderer.colour(99)
    assert colour == BLOCK_COLOURS[0]
