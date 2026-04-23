from __future__ import annotations

from typing import Any, Callable, Optional

import i18n  # type: ignore[import-untyped]
from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.gridlayout import GridLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.button import Button  # type: ignore[import-untyped]
from kivy.uix.scrollview import ScrollView  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.view.interfaces import IView
from OrecchietTetris.leaderboard.interfaces import ILeaderboardRepository


class LeaderboardScreen(Screen, IView):
    """Screen that displays the leaderboard table.

    Parameters
    ----------
    repository:
        The leaderboard repository to read entries from.
    on_back:
        Called (no arguments) when the player presses the back button.
    """

    def __init__(
        self,
        repository: ILeaderboardRepository,
        on_back: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._repo = repository
        self._on_back = on_back
        self._build_ui()

    # ------------------------------------------------------------------
    # IView
    # ------------------------------------------------------------------

    def show(self) -> None:
        self.opacity = 1.0
        self.disabled = False
        self._refresh_table()

    def hide(self) -> None:
        self.opacity = 0.0
        self.disabled = True

    def update(self, event_type: EventType, data: Any) -> None:
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        with self.canvas.before:
            Color(0.05, 0.05, 0.10, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = BoxLayout(orientation="vertical", padding=30, spacing=15)

        root.add_widget(Label(
            text=i18n.t("leaderboard"),
            font_size="36sp",
            bold=True,
            color=(0.9, 0.5, 0.1, 1),
            size_hint=(1, None),
            height=50,
        ))

        # Header row
        header = GridLayout(cols=5, size_hint=(1, None), height=36, spacing=4)
        for text in (i18n.t("rank"), i18n.t("name"), i18n.t("score"),
                     i18n.t("level"), i18n.t("lines")):
            header.add_widget(Label(
                text=text,
                bold=True,
                font_size="15sp",
                color=(0.9, 0.5, 0.1, 1),
            ))
        root.add_widget(header)

        # Scrollable table
        self._table = GridLayout(cols=5, spacing=4, size_hint_y=None)
        self._table.bind(minimum_height=self._table.setter("height"))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self._table)
        root.add_widget(scroll)

        btn_back = Button(
            text="\ue5c4",
            font_name="MaterialIcons",
            font_size="28sp",
            size_hint=(0.4, None),
            height=48,
            pos_hint={"center_x": 0.5},
            background_color=(0.3, 0.3, 0.7, 1),
        )
        btn_back.bind(on_release=self._handle_back)
        root.add_widget(btn_back)

        self.add_widget(root)

    def _refresh_table(self) -> None:
        self._table.clear_widgets()
        entries = self._repo.load_all()
        if not entries:
            self._table.add_widget(Label(
                text=i18n.t("empty_leaderboard"),
                font_size="16sp",
                color=(0.7, 0.7, 0.7, 1),
                size_hint_y=None,
                height=40,
            ))
            # fill remaining columns so the single-cell message spans correctly
            for _ in range(4):
                self._table.add_widget(Label(size_hint_y=None, height=40))
            return

        row_colors = [(0.12, 0.12, 0.18, 1), (0.08, 0.08, 0.14, 1)]
        for rank, entry in enumerate(entries, start=1):
            bg = row_colors[rank % 2]
            for val in (str(rank), entry.name, str(entry.score),
                        str(entry.level), str(entry.lines)):
                lbl = Label(
                    text=val,
                    font_size="14sp",
                    color=(1, 1, 1, 1),
                    size_hint_y=None,
                    height=34,
                )
                with lbl.canvas.before:
                    Color(*bg)
                    Rectangle(pos=lbl.pos, size=lbl.size)
                lbl.bind(
                    pos=lambda w, *_: self._redraw_row_bg(w),
                    size=lambda w, *_: self._redraw_row_bg(w),
                )
                self._table.add_widget(lbl)

    @staticmethod
    def _redraw_row_bg(widget: Any) -> None:
        widget.canvas.before.clear()

    def _handle_back(self, *_: Any) -> None:
        if self._on_back is not None:
            self._on_back()

    def _update_bg(self, *_: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
