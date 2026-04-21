from __future__ import annotations

from typing import Any

from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]

from OrecchietTetris.view.block_renderer import BLOCK_COLOURS


class Cell(Widget):
    """A single board cell drawn via canvas instructions."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        with self.canvas:
            # Layer 1: solid background (always the empty-cell colour for filled
            # cells so transparent image pixels match empty neighbours).
            self._color_instr = Color(*BLOCK_COLOURS[0])
            self._rect = Rectangle(pos=self.pos, size=self.size)
            # Layer 2: image drawn on top; hidden until set_texture is called.
            self._img_color = Color(1.0, 1.0, 1.0, 0.0)
            self._img_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._redraw, size=self._redraw)

    def set_colour(self, rgba: tuple[float, float, float, float]) -> None:
        self._color_instr.rgba = rgba
        self._rect.texture = None
        self._img_color.a = 0.0

    def set_texture(self, texture: object, alpha: float = 1.0) -> None:
        self._color_instr.rgba = BLOCK_COLOURS[0]
        self._rect.texture = None
        self._img_color.rgba = (1.0, 1.0, 1.0, alpha)
        self._img_rect.texture = texture
        self._img_rect.pos = self.pos
        self._img_rect.size = self.size

    def _redraw(self, *_: Any) -> None:
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._img_rect.pos = self.pos
        self._img_rect.size = self.size
