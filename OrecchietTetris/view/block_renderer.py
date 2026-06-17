from __future__ import annotations

from typing import Optional

from OrecchietTetris.utils.paths import ASSETS_DIR

# ---------------------------------------------------------------------------
# Mapping: tetromino colour integer → asset path
# ---------------------------------------------------------------------------
# The integers match the values used in ShapeType:
#   1 = I   2 = O   3 = T   4 = S   5 = Z   6 = J   7 = L
# ---------------------------------------------------------------------------

_SQUARES_DIR = ASSETS_DIR / "squares"

BLOCK_IMAGES: dict[int, str] = {i: str(_SQUARES_DIR / f"{i}.webp") for i in range(1, 8)}

# Colour used to tint shadow (ghost piece) cells
SHADOW_COLOUR: tuple[float, float, float, float] = (0.28, 0.28, 0.32, 1.0)

# RGBA colour for empty cells (fallback when no image is drawn)
EMPTY_COLOUR: tuple[float, float, float, float] = (0.1, 0.1, 0.1, 1.0)


class BlockRenderer:
    """Maps cell integers to Kivy canvas draw calls.

    Call ``preload_textures()`` once inside a live Kivy context (e.g. from
    ``GameScreen.__init__``) to upload all square images to the GPU.  Every
    subsequent ``texture()`` call is a plain dict lookup with no I/O.
    """

    def __init__(self) -> None:
        # CoreImage objects kept alive to pin their GL textures; GC would evict them otherwise.
        self._core_images: list[object] = []
        self._textures: dict[int, object] = {}

    def preload_textures(self) -> None:
        """Upload all block images to GPU once. Must be called inside a Kivy context."""
        if self._textures:
            return
        from pathlib import Path
        from kivy.core.image import Image as CoreImage  # type: ignore[import-untyped]
        for val, path in BLOCK_IMAGES.items():
            if Path(path).exists():
                img = CoreImage(path, mipmap=False)
                self._core_images.append(img)
                self._textures[val] = img.texture

    def texture(self, cell_value: int) -> Optional[object]:
        """Return the preloaded Kivy texture for *cell_value*, or *None*."""
        return self._textures.get(cell_value)

    def image_path(self, cell_value: int) -> Optional[str]:
        """Return the asset path for *cell_value*, or *None* for empty cells."""
        return BLOCK_IMAGES.get(cell_value)
