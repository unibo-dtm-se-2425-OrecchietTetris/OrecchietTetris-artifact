from __future__ import annotations

from typing import Any

from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.graphics import Color, RoundedRectangle, Line  # type: ignore[import-untyped]

_RADIUS = 14
_PADDING = [14, 10]
_SPACING = 4

_MEDAL: dict[int, tuple[float, float, float, float]] = {
    1: (1.00, 0.84, 0.00, 1.0),  # gold
    2: (0.75, 0.75, 0.75, 1.0),  # silver
    3: (0.80, 0.50, 0.20, 1.0),  # bronze
}
_MEDAL_BORDER: dict[int, tuple[float, float, float, float]] = {
    1: (1.00, 0.84, 0.00, 0.70),
    2: (0.75, 0.75, 0.75, 0.55),
    3: (0.80, 0.50, 0.20, 0.55),
}
_CARD_BG: dict[int, tuple[float, float, float, float]] = {
    1: (0.14, 0.13, 0.08, 1.0),  # warm dark
    2: (0.12, 0.12, 0.14, 1.0),  # cool dark
    3: (0.13, 0.10, 0.08, 1.0),  # warm dark
}
# Material Icons codepoint for "star" — safe on any platform where the font is loaded
_MEDAL_SYMBOL = {1: "", 2: "", 3: ""}
_MEDAL_FONT = "MaterialIcons"
# Heights: 1st is tallest to create the podium step effect
CARD_HEIGHTS: dict[int, int] = {1: 210, 2: 180, 3: 160}


class TopPlayerCard(BoxLayout):
    """Podium card for a top-3 player.

    Displays medal symbol, rank number, player name, score and level/lines
    with medal-coloured border and subtle background tint.  Intended to be
    placed inside an AnchorLayout(anchor_y="bottom") so all three cards sit
    on the same baseline, creating a classic podium step effect.
    """

    def __init__(
        self,
        rank: int,
        name: str,
        score: int,
        level: int,
        lines: int,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint", (1, None))
        kwargs.setdefault("height", CARD_HEIGHTS.get(rank, 140))
        kwargs.setdefault("padding", _PADDING)
        kwargs.setdefault("spacing", _SPACING)
        super().__init__(**kwargs)

        medal = _MEDAL[rank]
        border = _MEDAL_BORDER[rank]
        bg = _CARD_BG[rank]

        with self.canvas.before:
            Color(*bg)
            self._bg_rr = RoundedRectangle(pos=self.pos, size=self.size, radius=[_RADIUS])
            Color(*border)
            self._border_line = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, _RADIUS),
                width=2.0,
            )
        self.bind(pos=self._update_gfx, size=self._update_gfx)

        # Medal symbol — rendered with MaterialIcons to guarantee correct glyph
        self.add_widget(Label(
            text=_MEDAL_SYMBOL[rank],
            font_name=_MEDAL_FONT,
            font_size="26sp",
            color=medal,
            size_hint=(1, None),
            height=34,
        ))

        # Rank badge  (#1 / #2 / #3)
        self.add_widget(Label(
            text=f"#{rank}",
            font_size="12sp",
            bold=True,
            color=medal,
            size_hint=(1, None),
            height=18,
        ))

        # Player name
        name_lbl = Label(
            text=name,
            font_size="14sp",
            bold=True,
            color=(1.0, 1.0, 1.0, 1.0),
            size_hint=(1, None),
            height=22,
            halign="center",
            valign="middle",
        )
        name_lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.add_widget(name_lbl)

        # Score (prominent)
        self.add_widget(Label(
            text=f"{score:,}",
            font_size="17sp",
            bold=True,
            color=medal,
            size_hint=(1, None),
            height=26,
        ))

        # Level / Lines
        self.add_widget(Label(
            text=f"Lv.{level}  |  {lines}L",
            font_size="11sp",
            color=(0.60, 0.62, 0.72, 1.0),
            size_hint=(1, None),
            height=18,
        ))

    # ------------------------------------------------------------------

    def _update_gfx(self, *_: Any) -> None:
        self._bg_rr.pos = self.pos
        self._bg_rr.size = self.size
        self._border_line.rounded_rectangle = (
            self.x, self.y, self.width, self.height, _RADIUS
        )
