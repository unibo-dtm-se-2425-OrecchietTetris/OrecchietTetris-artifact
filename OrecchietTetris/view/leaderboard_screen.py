from __future__ import annotations

from typing import Any, Callable, Optional

import i18n  # type: ignore[import-untyped]
from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.anchorlayout import AnchorLayout  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.scrollview import ScrollView  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle, RoundedRectangle  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.view.interfaces import IView
from OrecchietTetris.view.widgets import RoundedButton, LeaderboardRow, TopPlayerCard
from OrecchietTetris.view.widgets.top_player_card import CARD_HEIGHTS
from OrecchietTetris.leaderboard.interfaces import ILeaderboardRepository
from OrecchietTetris.leaderboard.leaderboard_entry import LeaderboardEntry

_PODIUM_ROW_H = max(CARD_HEIGHTS.values()) + 10  # container height for the podium
_SECTION_H = 28


def _section_label(text: str) -> Label:
    """Styled divider label for tier sections."""
    return Label(
        text=text,
        font_size="12sp",
        bold=True,
        color=(0.40, 0.42, 0.58, 1.0),
        size_hint=(1, None),
        height=_SECTION_H,
        halign="left",
        valign="middle",
    )


class LeaderboardScreen(Screen, IView):
    """Game-like leaderboard screen.

    Layout
    ------
    * Title bar
    * Podium section (top-3 cards, step-aligned to bottom) when ≥ 3 entries
    * "Rankings" section header + scrollable card rows for rank 4+
    * Back button
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
        self._refresh()

    def hide(self) -> None:
        self.opacity = 0.0
        self.disabled = True

    def update(self, event_type: EventType, data: Any) -> None:
        pass

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def set_current_player(self, name: str) -> None:
        """Mark whose row should be highlighted on the next show()."""
        self._current_name = name

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._current_name: Optional[str] = None

        with self.canvas.before:
            Color(0.05, 0.05, 0.10, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self._root = BoxLayout(
            orientation="vertical",
            padding=[20, 16],
            spacing=10,
        )

        # Title
        self._root.add_widget(Label(
            text=i18n.t("leaderboard"),
            font_size="34sp",
            bold=True,
            color=(0.9, 0.5, 0.1, 1.0),
            size_hint=(1, None),
            height=48,
        ))

        # Podium placeholder (filled in _refresh)
        self._podium_container = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=0,
            spacing=6,
        )
        self._root.add_widget(self._podium_container)

        # Section label placeholder
        self._section_lbl = _section_label("")
        self._section_lbl.height = 0
        self._root.add_widget(self._section_lbl)

        # Scrollable rows
        self._rows_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=4,
        )
        self._rows_box.bind(minimum_height=self._rows_box.setter("height"))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self._rows_box)
        self._root.add_widget(scroll)

        # Back button
        btn_back = RoundedButton(
            text="",
            font_name="MaterialIcons",
            font_size="28sp",
            size_hint=(0.4, None),
            height=48,
            pos_hint={"center_x": 0.5},
            background_color=(0.3, 0.3, 0.7, 1),
        )
        btn_back.bind(on_release=self._handle_back)
        self._root.add_widget(btn_back)

        self.add_widget(self._root)

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        entries = self._repo.load_all()
        self._podium_container.clear_widgets()
        self._rows_box.clear_widgets()

        if not entries:
            self._podium_container.height = 0
            self._section_lbl.text = ""
            self._section_lbl.height = 0
            self._rows_box.add_widget(Label(
                text=i18n.t("empty_leaderboard"),
                font_size="16sp",
                color=(0.55, 0.55, 0.65, 1.0),
                size_hint_y=None,
                height=50,
            ))
            return

        top3 = entries[:3]
        rest = entries[3:]

        # ── Podium (top-3) ────────────────────────────────────────────
        if len(top3) >= 3:
            self._build_podium(top3)
        else:
            self._podium_container.height = 0
            for i, entry in enumerate(top3):
                self._rows_box.add_widget(self._make_row(i + 1, entry))

        # ── Rankings list (rank 4+) ───────────────────────────────────
        if rest:
            self._section_lbl.text = f"— {i18n.t('rankings')} —"
            self._section_lbl.height = _SECTION_H
        else:
            self._section_lbl.text = ""
            self._section_lbl.height = 0

        for i, entry in enumerate(rest):
            self._rows_box.add_widget(self._make_row(i + 4, entry, alt=(i % 2 == 1)))

    def _build_podium(self, top3: list[LeaderboardEntry]) -> None:
        """Arrange top-3 as a podium: 2nd | 1st | 3rd aligned to bottom."""
        # Order: 2nd left, 1st center, 3rd right
        order = [(2, top3[1]), (1, top3[0]), (3, top3[2])]

        podium_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=_PODIUM_ROW_H,
            spacing=6,
        )
        for rank, entry in order:
            anchor = AnchorLayout(anchor_x="center", anchor_y="bottom", size_hint=(1, 1))
            card = TopPlayerCard(
                rank=rank,
                name=entry.name,
                score=entry.score,
                level=entry.level,
                lines=entry.lines,
            )
            anchor.add_widget(card)
            podium_row.add_widget(anchor)

        self._podium_container.add_widget(podium_row)
        self._podium_container.height = _PODIUM_ROW_H

    def _make_row(self, rank: int, entry: LeaderboardEntry, alt: bool = False) -> LeaderboardRow:
        highlighted = (
            self._current_name is not None
            and entry.name == self._current_name
        )
        return LeaderboardRow(
            rank=rank,
            name=entry.name,
            score=entry.score,
            level=entry.level,
            lines=entry.lines,
            highlighted=highlighted,
            alt=alt,
        )

    # ------------------------------------------------------------------

    def _handle_back(self, *_: Any) -> None:
        if self._on_back is not None:
            self._on_back()

    def _update_bg(self, *_: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
