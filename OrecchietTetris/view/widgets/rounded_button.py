from __future__ import annotations

from typing import Any

from kivy.uix.button import Button  # type: ignore[import-untyped]
from kivy.graphics import Color, RoundedRectangle  # type: ignore[import-untyped]

_RADIUS: list[int] = [12]


class RoundedButton(Button):
    """Button with 10 dp rounded corners drawn via canvas.before."""

    def __init__(self, **kwargs: Any) -> None:
        color: Any = kwargs.pop('background_color', (0.5, 0.5, 0.5, 1.0))
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._bg_color_instr: Color = Color(*color)
            self._bg_rrect: RoundedRectangle = RoundedRectangle(
                pos=self.pos, size=self.size, radius=_RADIUS,
            )
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *_: Any) -> None:
        self._bg_rrect.pos = self.pos
        self._bg_rrect.size = self.size

    def set_color(self, rgba: tuple[float, float, float, float]) -> None:
        self._bg_color_instr.rgba = rgba
