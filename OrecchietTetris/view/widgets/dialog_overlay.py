from __future__ import annotations

from typing import Any, Callable, Optional

from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.uix.floatlayout import FloatLayout  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line  # type: ignore[import-untyped]

from OrecchietTetris.view.widgets.rounded_button import RoundedButton

_CARD_WIDTH = 340
_CARD_PADDING = 24
_CARD_SPACING = 14
_LABEL_H = 46
_BUTTON_H = 52
_CARD_RADIUS = 20


class DialogOverlay(FloatLayout):
    """Full-screen modal overlay with a centered rounded dialog card.

    Usage::

        dlg = DialogOverlay(title="Game Over", title_color=(0.9, 0.2, 0.2, 1))
        dlg.add_label("Score: 1234", font_size="24sp")
        dlg.add_button("Try Again", bg=(0.2, 0.7, 0.2, 1), on_release=handler)
        self.add_widget(dlg)
    """

    def __init__(
        self,
        title: str = "",
        title_color: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("size_hint", (1, 1))
        super().__init__(**kwargs)

        # Full-screen dark scrim
        with self.canvas.before:
            Color(0, 0, 0, 0.75)
            self._scrim = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_scrim, size=self._update_scrim)

        # Card container (centered)
        self._card = BoxLayout(
            orientation="vertical",
            spacing=_CARD_SPACING,
            padding=[_CARD_PADDING, _CARD_PADDING],
            size_hint=(None, None),
            width=_CARD_WIDTH,
            height=_CARD_PADDING * 2,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        with self._card.canvas.before:
            Color(0.10, 0.10, 0.18, 1)
            self._card_bg = RoundedRectangle(
                pos=self._card.pos, size=self._card.size, radius=[_CARD_RADIUS]
            )
            Color(0.38, 0.38, 0.58, 1)
            self._card_border = Line(
                rounded_rectangle=(
                    self._card.x, self._card.y,
                    self._card.width, self._card.height,
                    _CARD_RADIUS,
                ),
                width=1.5,
            )
        self._card.bind(pos=self._update_card_gfx, size=self._update_card_gfx)

        if title:
            lbl = Label(
                text=title,
                font_size="30sp",
                bold=True,
                color=title_color,
                size_hint=(1, None),
                height=_LABEL_H + 10,
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lambda inst, s: setattr(inst, "text_size", s))
            self._card.add_widget(lbl)
            self._grow_card(_LABEL_H + 10)

        self.add_widget(self._card)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_label(
        self,
        text: str,
        font_size: str = "22sp",
        color: tuple[float, float, float, float] = (1, 1, 1, 1),
    ) -> Label:
        lbl = Label(
            text=text,
            font_size=font_size,
            color=color,
            size_hint=(1, None),
            height=_LABEL_H,
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lambda inst, s: setattr(inst, "text_size", s))
        self._card.add_widget(lbl)
        self._grow_card(_LABEL_H)
        return lbl

    def add_generic_widget(self, widget: Widget, height: int) -> None:
        self._card.add_widget(widget)
        self._grow_card(height)

    def add_button(
        self,
        text: str,
        bg: tuple[float, float, float, float],
        on_release: Callable[..., Any],
        font_name: Optional[str] = None,
        font_size: str = "22sp",
    ) -> RoundedButton:
        kwargs: dict[str, Any] = dict(
            text=text,
            markup=True,
            font_size=font_size,
            size_hint=(0.85, None),
            height=_BUTTON_H,
            pos_hint={"center_x": 0.5},
            background_color=bg,
        )
        if font_name:
            kwargs["font_name"] = font_name
        btn = RoundedButton(**kwargs)
        btn.bind(on_release=on_release)
        self._card.add_widget(btn)
        self._grow_card(_BUTTON_H)
        return btn

    def add_button_row(
        self,
        buttons: list[dict[str, Any]],
    ) -> BoxLayout:
        """Add a horizontal row of buttons.  Each dict is passed as kwargs to add_button."""
        row = BoxLayout(
            orientation="horizontal",
            size_hint=(0.85, None),
            height=_BUTTON_H,
            pos_hint={"center_x": 0.5},
            spacing=12,
        )
        for spec in buttons:
            on_release = spec.pop("on_release")
            bg = spec.pop("bg")
            text = spec.pop("text")
            font_name = spec.pop("font_name", None)
            font_size = spec.pop("font_size", "22sp")
            bkwargs: dict[str, Any] = dict(
                text=text,
                font_size=font_size,
                background_color=bg,
            )
            if font_name:
                bkwargs["font_name"] = font_name
            btn = RoundedButton(**bkwargs)
            btn.bind(on_release=on_release)
            row.add_widget(btn)
        self._card.add_widget(row)
        self._grow_card(_BUTTON_H)
        return row

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _grow_card(self, added_h: float) -> None:
        n = len(self._card.children)
        extra_spacing = _CARD_SPACING if n > 1 else 0
        self._card.height += added_h + extra_spacing

    def _update_scrim(self, *_: Any) -> None:
        self._scrim.pos = self.pos
        self._scrim.size = self.size

    def _update_card_gfx(self, *_: Any) -> None:
        self._card_bg.pos = self._card.pos
        self._card_bg.size = self._card.size
        self._card_border.rounded_rectangle = (
            self._card.x, self._card.y,
            self._card.width, self._card.height,
            _CARD_RADIUS,
        )
