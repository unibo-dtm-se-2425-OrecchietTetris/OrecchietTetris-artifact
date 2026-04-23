from __future__ import annotations

from typing import Any, Optional

from kivy.uix.widget import Widget  # type: ignore[import-untyped]

from OrecchietTetris.view.block_renderer import BlockRenderer, EMPTY_COLOUR
from OrecchietTetris.view.widgets.cell import Cell


class PiecePreview(Widget):
    """Renders a preview of a tetromino shape in a grid."""

    PREVIEW_COLS = 6
    PREVIEW_ROWS = 6
    CELL = PREVIEW_ROWS * PREVIEW_COLS

    def __init__(self, renderer: BlockRenderer, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._renderer = renderer
        self._cells: list[list[Cell]] = []
        self._build()

    def _build(self) -> None:
        for _ in range(self.PREVIEW_ROWS):
            row_cells: list[Cell] = []
            for _ in range(self.PREVIEW_COLS):
                cell = Cell(size_hint=(None, None))
                self.add_widget(cell)
                row_cells.append(cell)
            self._cells.append(row_cells)
        self.bind(pos=self._reposition, size=self._reposition)

    def _reposition(self, *_: Any) -> None:
        cs = min(self.width / self.PREVIEW_COLS, self.height / self.PREVIEW_ROWS)
        x_off = (self.width - cs * self.PREVIEW_COLS) / 2
        y_off = (self.height - cs * self.PREVIEW_ROWS) / 2
        for r, row_cells in enumerate(self._cells):
            for c, cell in enumerate(row_cells):
                cell.size = (cs, cs)
                cell.pos = (
                    self.x + x_off + c * cs,
                    self.y + y_off + (self.PREVIEW_ROWS - 1 - r) * cs,
                )

    def set_piece(self, shape: Optional[list[list[Any]]], greyed: bool = False) -> None:
        """Render *shape* centred in the preview grid. *shape=None* clears."""
        for row_cells in self._cells:
            for cell in row_cells:
                cell.set_colour(EMPTY_COLOUR)

        if shape is None:
            return

        row_offset = (self.PREVIEW_ROWS - len(shape)) // 2
        col_offset = (self.PREVIEW_COLS - len(shape[0])) // 2
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                pr = row_offset + r
                pc = col_offset + c
                if 0 <= pr < self.PREVIEW_ROWS and 0 <= pc < self.PREVIEW_COLS and val != 0:
                    tex = self._renderer.texture(val)
                    if tex is not None:
                        self._cells[pr][pc].set_texture(tex, alpha=0.35 if greyed else 1.0)
                    else:
                        rgba = self._renderer.colour(val)
                        if greyed:
                            rgba = (rgba[0] * 0.4, rgba[1] * 0.4, rgba[2] * 0.4, 0.6)
                        self._cells[pr][pc].set_colour(rgba)
