from __future__ import annotations

from typing import Any, Callable, Optional

from kivy.uix.screenmanager import Screen  # type: ignore[import]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import]
from kivy.uix.button import Button  # type: ignore[import]
from kivy.uix.label import Label  # type: ignore[import]
from kivy.uix.togglebutton import ToggleButton  # type: ignore[import]
from kivy.graphics import Color, Rectangle  # type: ignore[import]

from OrecchietTetris.utils import EventType
from OrecchietTetris.view.interfaces import IView
from OrecchietTetris.view.i18n import I18n


class MenuScreen(Screen, IView):
    """Main menu screen.

    Shows a *New Game* button and a language toggle (EN / IT).
    All text is sourced from the ``I18n`` instance so switching the language
    refreshes labels immediately.

    Parameters
    ----------
    i18n:
        Shared localization instance.
    on_new_game:
        Called (no arguments) when the player presses *New Game*.
    """

    def __init__(
        self,
        i18n: I18n,
        on_new_game: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._i18n = i18n
        self._on_new_game = on_new_game
        self._build_ui()

    # ------------------------------------------------------------------
    # IView
    # ------------------------------------------------------------------

    def show(self) -> None:
        self.opacity = 1.0
        self.disabled = False

    def hide(self) -> None:
        self.opacity = 0.0
        self.disabled = True

    def update(self, event_type: EventType, data: Any) -> None:
        # The menu screen does not react to game events.
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construct all child widgets."""
        with self.canvas.before:
            Color(0.05, 0.05, 0.10, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

        root = BoxLayout(orientation="vertical", padding=40, spacing=20)

        # Title
        title = Label(
            text="OrecchietTetris",
            font_size="48sp",
            bold=True,
            color=(0.9, 0.5, 0.1, 1),
            size_hint=(1, 0.3),
        )
        root.add_widget(title)

        # New-game button
        self._btn_new_game = Button(
            text=self._i18n.t("new_game"),
            font_size="28sp",
            size_hint=(0.5, 0.15),
            pos_hint={"center_x": 0.5},
            background_color=(0.9, 0.5, 0.1, 1),
            color=(0.05, 0.05, 0.10, 1),
        )
        self._btn_new_game.bind(on_release=self._handle_new_game)
        root.add_widget(self._btn_new_game)

        # Language row
        lang_row = BoxLayout(orientation="horizontal", size_hint=(0.5, 0.1),
                             pos_hint={"center_x": 0.5}, spacing=10)

        lang_label = Label(
            text=self._i18n.t("language") + ":",
            font_size="20sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(0.4, 1),
        )
        self._lang_label = lang_label
        lang_row.add_widget(lang_label)

        self._btn_en = ToggleButton(
            text="EN",
            group="language",
            state="down" if self._i18n.language == "en" else "normal",
            font_size="18sp",
            size_hint=(0.3, 1),
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_it = ToggleButton(
            text="IT",
            group="language",
            state="down" if self._i18n.language == "it" else "normal",
            font_size="18sp",
            size_hint=(0.3, 1),
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_en.bind(on_release=lambda _: self._set_language("en"))
        self._btn_it.bind(on_release=lambda _: self._set_language("it"))
        lang_row.add_widget(self._btn_en)
        lang_row.add_widget(self._btn_it)
        root.add_widget(lang_row)

        self.add_widget(root)

    def _update_bg(self, *_args: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _handle_new_game(self, *_args: Any) -> None:
        if self._on_new_game is not None:
            self._on_new_game()

    def _set_language(self, lang: str) -> None:
        self._i18n.set_language(lang)
        self._refresh_labels()

    def _refresh_labels(self) -> None:
        self._btn_new_game.text = self._i18n.t("new_game")
        self._lang_label.text = self._i18n.t("language") + ":"
