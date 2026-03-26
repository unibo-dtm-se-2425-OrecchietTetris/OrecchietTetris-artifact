from __future__ import annotations

import os
from typing import Optional

# ---------------------------------------------------------------------------
# Mapping: tetromino colour integer → asset path
# ---------------------------------------------------------------------------
# The integers match the values used in ShapeType:
#   1 = I (cyan)   2 = O (yellow)  3 = T (purple)  4 = S (green)
#   5 = Z (red)    6 = J (blue)    7 = L (orange)
# ---------------------------------------------------------------------------

BLOCK_IMAGES: dict[int, str] = {
    1: os.path.join("assets", "blocks", "I.png"),
    2: os.path.join("assets", "blocks", "O.png"),
    3: os.path.join("assets", "blocks", "T.png"),
    4: os.path.join("assets", "blocks", "S.png"),
    5: os.path.join("assets", "blocks", "Z.png"),
    6: os.path.join("assets", "blocks", "J.png"),
    7: os.path.join("assets", "blocks", "L.png"),
}

# Colour used to tint shadow (ghost piece) cells
SHADOW_COLOUR: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.25)

# RGBA colours used as a fallback when image files are absent
BLOCK_COLOURS: dict[int, tuple[float, float, float, float]] = {
    0: (0.1, 0.1, 0.1, 1.0),   # empty cell
    1: (0.0, 0.9, 0.9, 1.0),   # I – cyan
    2: (0.9, 0.9, 0.0, 1.0),   # O – yellow
    3: (0.6, 0.0, 0.9, 1.0),   # T – purple
    4: (0.0, 0.9, 0.0, 1.0),   # S – green
    5: (0.9, 0.0, 0.0, 1.0),   # Z – red
    6: (0.0, 0.0, 0.9, 1.0),   # J – blue
    7: (0.9, 0.45, 0.0, 1.0),  # L – orange
}


class BlockRenderer:
    """Maps cell integers to Kivy ``Image`` widgets or canvas draw calls.

    Usage (Kivy widget context)::

        renderer = BlockRenderer()
        widget = renderer.image_widget(cell_value)   # returns kivy Image
        colour  = renderer.colour(cell_value)        # returns RGBA 4-tuple

    The ``image_widget`` method is intentionally lazy-imported so that this
    module can be imported without a running Kivy environment (e.g. in tests).
    """

    def image_widget(self, cell_value: int, size: tuple[int, int] = (32, 32)) -> object:
        """Return a Kivy ``Image`` widget for *cell_value*.

        Falls back to a ``Button``-styled widget coloured via ``BLOCK_COLOURS``
        if the asset file does not exist.
        """
        from kivy.uix.image import Image  # type: ignore[import-untyped]
        from kivy.uix.widget import Widget  # type: ignore[import-untyped]
        from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]

        source = BLOCK_IMAGES.get(cell_value)
        if source and os.path.exists(source):
            return Image(source=source, size=size, size_hint=(None, None))

        # Fallback: plain coloured rectangle widget
        w = Widget(size=size, size_hint=(None, None))
        r, g, b, a = self.colour(cell_value)
        with w.canvas:
            Color(r, g, b, a)
            Rectangle(pos=w.pos, size=w.size)
        return w

    def colour(self, cell_value: int) -> tuple[float, float, float, float]:
        """Return the RGBA 4-tuple for *cell_value* (0 = empty)."""
        return BLOCK_COLOURS.get(cell_value, BLOCK_COLOURS[0])

    def shadow_colour(self) -> tuple[float, float, float, float]:
        """Return the RGBA colour used for shadow (ghost piece) cells."""
        return SHADOW_COLOUR

    def image_path(self, cell_value: int) -> Optional[str]:
        """Return the asset path for *cell_value*, or *None* for empty cells."""
        return BLOCK_IMAGES.get(cell_value)
