from __future__ import annotations

from OrecchietTetris.view.widgets.top_player_card import CARD_HEIGHTS


def test_card_heights_has_exactly_three_ranks() -> None:
    assert set(CARD_HEIGHTS.keys()) == {1, 2, 3}


def test_first_place_is_tallest() -> None:
    assert CARD_HEIGHTS[1] > CARD_HEIGHTS[2]
    assert CARD_HEIGHTS[1] > CARD_HEIGHTS[3]


def test_second_place_taller_than_third() -> None:
    assert CARD_HEIGHTS[2] > CARD_HEIGHTS[3]


def test_all_heights_positive() -> None:
    assert all(h > 0 for h in CARD_HEIGHTS.values())


def test_top_player_card_exported_from_widgets_package() -> None:
    from OrecchietTetris.view.widgets import TopPlayerCard  # noqa: F401
