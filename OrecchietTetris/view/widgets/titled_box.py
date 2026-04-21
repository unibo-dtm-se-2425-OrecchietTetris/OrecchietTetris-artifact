from __future__ import annotations

from typing import Any, Optional

from kivy.uix.widget import Widget  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.graphics import Color, Line  # type: ignore[import-untyped]


class TitledBox(Widget):
    """A bordered panel with an optional bold title label inside at the top."""

    _TITLE_H: int = 20
    _PAD: int = 12

    def __init__(self, title: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._title_str = title
        self._content_widget: Optional[Widget] = None

        with self.canvas:
            Color(0.35, 0.35, 0.55, 1)
            self._border_instr = Line(width=1.5)

        self._lbl = Label(
            text=title or "",
            font_size="13sp",
            bold=True,
            color=(0.70, 0.70, 0.90, 1),
            size_hint=(None, None),
            size=(80, self._TITLE_H),
            opacity=1 if title else 0,
        )
        self.add_widget(self._lbl)
        self.bind(pos=self._layout, size=self._layout)

    def set_title(self, text: Optional[str]) -> None:
        self._title_str = text
        self._lbl.text = text or ""
        self._lbl.opacity = 1 if text else 0
        self._layout()

    def set_content(self, widget: Widget) -> None:
        self._content_widget = widget
        self.add_widget(widget)
        self._layout()

    def _layout(self, *_: Any) -> None:
        th = self._TITLE_H
        pad = self._PAD
        x, y, w, h = self.x, self.y, self.width, self.height

        self._border_instr.rounded_rectangle = (x + 1, y + 1, w - 2, h - 2, 20)

        if self._title_str:
            lbl_w = max(60, min(w - 2 * pad, len(self._title_str) * 9 + 20))
            self._lbl.size = (lbl_w, th)
            self._lbl.pos = (x + (w - lbl_w) / 2, y + h - pad - th)
            content_h = h - th - 3 * pad
        else:
            content_h = h - 2 * pad

        if self._content_widget is not None:
            self._content_widget.size = (w - 2 * pad, content_h)
            self._content_widget.pos = (x + pad, y + pad)
