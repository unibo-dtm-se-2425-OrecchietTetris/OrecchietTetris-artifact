from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.graphics import Color, RoundedRectangle, Line  # type: ignore[import-untyped]

_RADIUS = 10
_PADDING = [10, 5]
_SPACING = 8

# Medal colours for top-3
_MEDAL: dict[int, tuple[float, float, float, float]] = {
    1: (1.00, 0.84, 0.00, 1.0),  # gold
    2: (0.75, 0.75, 0.75, 1.0),  # silver
    3: (0.80, 0.50, 0.20, 1.0),  # bronze
}
_MEDAL_BORDER: dict[int, tuple[float, float, float, float]] = {
    1: (1.00, 0.84, 0.00, 0.55),
    2: (0.75, 0.75, 0.75, 0.45),
    3: (0.80, 0.50, 0.20, 0.45),
}
_BG_NORMAL = (0.10, 0.12, 0.20, 1.0)
_BG_ALT = (0.08, 0.10, 0.17, 1.0)
_BG_HIGHLIGHT = (0.10, 0.22, 0.42, 1.0)
_BORDER_NORMAL = (0.20, 0.22, 0.35, 0.35)
_BORDER_HIGHLIGHT = (0.30, 0.60, 1.00, 0.80)

_UP_COLOR = (0.30, 0.90, 0.30, 1.0)
_DOWN_COLOR = (0.90, 0.30, 0.30, 1.0)
_SAME_COLOR = (0.45, 0.45, 0.55, 1.0)


class LeaderboardRow(BoxLayout):
    """Card-style leaderboard row.

    Shows rank badge, player name, score, level/lines stats and an optional
    rank-change arrow.  Top-3 ranks receive medal-coloured badge and border;
    the current-player row is highlighted in blue.
    """

    HEIGHT: int = 54

    def __init__(
        self,
        rank: int,
        name: str,
        score: int,
        level: int,
        lines: int,
        rank_change: int = 0,
        highlighted: bool = False,
        alt: bool = False,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", self.HEIGHT)
        kwargs.setdefault("padding", _PADDING)
        kwargs.setdefault("spacing", _SPACING)
        super().__init__(**kwargs)

        is_top3 = rank in _MEDAL

        # Background & border colours
        if highlighted:
            bg = _BG_HIGHLIGHT
            border = _BORDER_HIGHLIGHT
            border_w = 1.5
        elif is_top3:
            bg = (0.11, 0.11, 0.19, 1.0)
            border = _MEDAL_BORDER[rank]
            border_w = 1.5
        else:
            bg = _BG_ALT if alt else _BG_NORMAL
            border = _BORDER_NORMAL
            border_w = 0.8

        with self.canvas.before:
            Color(*bg)
            self._bg_rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[_RADIUS])
            Color(*border)
            self._border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, _RADIUS),
                width=border_w,
            )
        self.bind(pos=self._update_gfx, size=self._update_gfx)

        # ── Rank badge ───────────────────────────────────────────────
        badge_box = BoxLayout(size_hint=(None, 1), width=44)
        medal_color = _MEDAL.get(rank)
        if medal_color is not None:
            with badge_box.canvas.before:
                Color(*medal_color)
                _rr = RoundedRectangle(pos=badge_box.pos, size=badge_box.size, radius=[8])
            badge_box.bind(
                pos=lambda w, *_, r=_rr: setattr(r, "pos", w.pos),
                size=lambda w, *_, r=_rr: setattr(r, "size", w.size),
            )
        badge_box.add_widget(Label(
            text=str(rank),
            font_size="15sp",
            bold=True,
            color=(0.0, 0.0, 0.0, 1.0) if medal_color else (0.60, 0.62, 0.72, 1.0),
        ))
        self.add_widget(badge_box)

        # ── Name ─────────────────────────────────────────────────────
        name_color = (0.45, 0.75, 1.00, 1.0) if highlighted else (1.0, 1.0, 1.0, 1.0)
        name_lbl = Label(
            text=name,
            font_size="15sp",
            bold=highlighted or is_top3,
            color=name_color,
            size_hint=(1, 1),
            halign="left",
            valign="middle",
        )
        name_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(name_lbl)

        # ── Score ─────────────────────────────────────────────────────
        score_color = _MEDAL.get(rank, (0.90, 0.85, 0.70, 1.0))
        score_lbl = Label(
            text=f"{score:,}",
            font_size="15sp",
            bold=is_top3,
            color=score_color,
            size_hint=(None, 1),
            width=96,
            halign="right",
            valign="middle",
        )
        score_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(score_lbl)

        # ── Level / Lines ─────────────────────────────────────────────
        stats_lbl = Label(
            text=f"Lv.{level}  {lines}L",
            font_size="11sp",
            color=(0.55, 0.58, 0.68, 1.0),
            size_hint=(None, 1),
            width=72,
            halign="center",
            valign="middle",
        )
        stats_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(stats_lbl)

        # ── Rank-change arrow ─────────────────────────────────────────
        if rank_change > 0:
            ch_text = f"▲{rank_change}"
            ch_color = _UP_COLOR
        elif rank_change < 0:
            ch_text = f"▼{abs(rank_change)}"
            ch_color = _DOWN_COLOR
        else:
            ch_text = "—"
            ch_color = _SAME_COLOR
        self.add_widget(Label(
            text=ch_text,
            font_size="12sp",
            color=ch_color,
            size_hint=(None, 1),
            width=36,
        ))

    # ------------------------------------------------------------------

    def _update_gfx(self, *_: Any) -> None:
        self._bg_rr.pos = self.pos
        self._bg_rr.size = self.size
        self._border_line.rounded_rectangle = (
            self.x, self.y, self.width, self.height, _RADIUS
        )
