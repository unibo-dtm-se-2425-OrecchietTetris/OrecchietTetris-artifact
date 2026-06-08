"""Tests for TopPlayerCard.

TopPlayerCard is a podium-step card for a top-3 player.  Each rank gets a
specific height, medal colour, and border colour.  The classic podium step
effect is achieved by placing the three cards in an AnchorLayout(anchor_y="bottom").
"""
from __future__ import annotations

from OrecchietTetris.view.widgets.top_player_card import (
    TopPlayerCard,
    CARD_HEIGHTS,
)


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


# ---------------------------------------------------------------------------
# Construction — lines 53-119
# ---------------------------------------------------------------------------

def test_top_player_card_rank1_can_be_instantiated() -> None:
    card = TopPlayerCard(rank=1, name="Gold", score=10000, level=8, lines=80)
    assert card is not None


def test_top_player_card_rank2_can_be_instantiated() -> None:
    card = TopPlayerCard(rank=2, name="Silver", score=8000, level=6, lines=60)
    assert card is not None


def test_top_player_card_rank3_can_be_instantiated() -> None:
    card = TopPlayerCard(rank=3, name="Bronze", score=6000, level=5, lines=50)
    assert card is not None


def test_top_player_card_rank1_height_matches_constant() -> None:
    card = TopPlayerCard(rank=1, name="A", score=0, level=1, lines=0)
    assert card.height == CARD_HEIGHTS[1]


def test_top_player_card_rank2_height_matches_constant() -> None:
    card = TopPlayerCard(rank=2, name="B", score=0, level=1, lines=0)
    assert card.height == CARD_HEIGHTS[2]


def test_top_player_card_rank3_height_matches_constant() -> None:
    card = TopPlayerCard(rank=3, name="C", score=0, level=1, lines=0)
    assert card.height == CARD_HEIGHTS[3]


def test_top_player_card_has_gfx_instructions() -> None:
    card = TopPlayerCard(rank=1, name="X", score=1000, level=3, lines=10)
    assert hasattr(card, "_bg_rr")
    assert hasattr(card, "_border_line")


# ---------------------------------------------------------------------------
# _update_gfx — lines 130-132
# ---------------------------------------------------------------------------

def test_update_gfx_syncs_to_pos_and_size() -> None:
    """_update_gfx must propagate new pos/size to background rect and border."""
    card = TopPlayerCard(rank=2, name="X", score=500, level=2, lines=10)
    card.pos = (5, 10)
    card.size = (200, CARD_HEIGHTS[2])
    card._update_gfx()
    assert card._bg_rr.pos == (5, 10)
    assert card._bg_rr.size == (200, CARD_HEIGHTS[2])
