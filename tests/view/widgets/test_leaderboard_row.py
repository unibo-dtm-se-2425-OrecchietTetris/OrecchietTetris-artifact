from __future__ import annotations

from OrecchietTetris.view.widgets.leaderboard_row import LeaderboardRow


def test_height_constant() -> None:
    assert LeaderboardRow.HEIGHT == 54


def test_leaderboard_row_exported_from_widgets_package() -> None:
    from OrecchietTetris.view.widgets import LeaderboardRow as LR
    assert LR is LeaderboardRow
