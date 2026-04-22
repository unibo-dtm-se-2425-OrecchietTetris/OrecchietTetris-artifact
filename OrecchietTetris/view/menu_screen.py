from __future__ import annotations

from typing import Any, Callable, Optional

import i18n  # type: ignore[import-untyped]
from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.button import Button  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.slider import Slider  # type: ignore[import-untyped]
from kivy.uix.togglebutton import ToggleButton  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]
from kivy.app import App  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.view.interfaces import IView
from OrecchietTetris.audio.interfaces import IAudioController


class MenuScreen(Screen, IView):
    """Main menu screen.

    Parameters
    ----------
    on_new_game:
        Called (no arguments) when the player presses *New Game*.
    audio:
        Optional audio controller; exposes a volume slider when provided.
    """

    def __init__(
        self,
        on_new_game: Optional[Callable[[], None]] = None,
        audio: Optional[IAudioController] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._on_new_game = on_new_game
        self._audio = audio
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
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
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
            text=f"[font=MaterialIcons]\ue037[/font]  {i18n.t('new_game')}",
            markup=True,
            font_size="28sp",
            size_hint=(0.5, 0.15),
            pos_hint={"center_x": 0.5},
            background_color=(0.9, 0.5, 0.1, 1),
        )
        self._btn_new_game.bind(on_release=self._handle_new_game)
        root.add_widget(self._btn_new_game)

        # Volume row (only when an audio controller is provided)
        if self._audio is not None:
            vol_row = BoxLayout(
                orientation="horizontal",
                size_hint=(0.6, None),
                height=40,
                pos_hint={"center_x": 0.5},
                spacing=10,
            )
            self._lbl_volume = Label(
                text=f"[font=MaterialIcons]\ue050[/font]  {i18n.t('volume')}",
                markup=True,
                font_size="18sp",
                color=(0.8, 0.8, 0.8, 1),
                size_hint=(0.4, 1),
            )
            vol_row.add_widget(self._lbl_volume)
            self._slider_volume = Slider(
                min=0.0,
                max=1.0,
                value=self._audio.volume,
                size_hint=(0.6, 1),
                cursor_size=(20, 20),
            )
            self._slider_volume.bind(value=self._on_volume_change)
            vol_row.add_widget(self._slider_volume)
            root.add_widget(vol_row)

        # Language row
        lang_row = BoxLayout(orientation="horizontal", size_hint=(0.5, 0.1),
                             pos_hint={"center_x": 0.5}, spacing=10)

        lang_label = Label(
            text=i18n.t("language") + ":",
            font_size="20sp",
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(0.4, 1),
        )
        self._lang_label = lang_label
        lang_row.add_widget(lang_label)

        self._btn_en = ToggleButton(
            text="EN",
            group="language",
            state="down" if str(i18n.get('locale')) == "en" else "normal",
            font_size="18sp",
            size_hint=(0.3, 1),
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_it = ToggleButton(
            text="IT",
            group="language",
            state="down" if str(i18n.get('locale')) == "it" else "normal",
            font_size="18sp",
            size_hint=(0.3, 1),
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_en.bind(on_release=lambda _: self._set_language("en"))
        self._btn_it.bind(on_release=lambda _: self._set_language("it"))
        lang_row.add_widget(self._btn_en)
        lang_row.add_widget(self._btn_it)
        root.add_widget(lang_row)

        # Quit button
        self._btn_quit = Button(
            text="\ue9ba",
            font_name="MaterialIcons",
            font_size="28sp",
            size_hint=(0.5, 0.12),
            pos_hint={"center_x": 0.5},
            background_color=(0.7, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
        )
        self._btn_quit.bind(on_release=self._handle_quit)
        root.add_widget(self._btn_quit)

        self.add_widget(root)

    def _on_volume_change(self, _slider: Any, value: float) -> None:
        if self._audio is not None:
            self._audio.set_volume(value)

    def _handle_quit(self, *_args: Any) -> None:
        App.get_running_app().stop()

    def _update_bg(self, *_args: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _handle_new_game(self, *_args: Any) -> None:
        if self._on_new_game is not None:
            self._on_new_game()

    def _set_language(self, lang: str) -> None:
        i18n.set('locale', lang)
        self._refresh_labels()

    def _refresh_labels(self) -> None:
        self._btn_new_game.text = f"[font=MaterialIcons]\ue037[/font]  {i18n.t('new_game')}"
        self._lang_label.text = i18n.t("language") + ":"
        if self._audio is not None:
            self._lbl_volume.text = f"[font=MaterialIcons]\ue050[/font]  {i18n.t('volume')}"
