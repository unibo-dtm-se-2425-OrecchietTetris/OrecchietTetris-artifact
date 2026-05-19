from __future__ import annotations

from typing import Any, Callable, Optional

import i18n  # type: ignore[import-untyped]
from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.image import Image  # type: ignore[import-untyped]
from kivy.uix.slider import Slider  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]
from kivy.app import App  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.view.interfaces import IView
from OrecchietTetris.audio.interfaces import IAudioController
from OrecchietTetris.view.widgets import RoundedButton, RoundedToggleButton, DialogOverlay

_BUTTON_H = 52   # matches DialogOverlay._BUTTON_H
_ICON_BTN_SIZE = 56  # transparent corner icon buttons

_IC_PLAY = ""
_IC_STAR = ""      # leaderboard
_IC_GEAR = ""      # settings
_IC_QUIT = ""      # exit
_IC_VOL = ""       # volume_up
_IC_MUTE = ""    # volume_off


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
        on_leaderboard: Optional[Callable[[], None]] = None,
        audio: Optional[IAudioController] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._on_new_game = on_new_game
        self._on_leaderboard = on_leaderboard
        self._audio = audio
        self._settings_overlay: Optional[DialogOverlay] = None
        self._btn_volume: Optional[RoundedButton] = None
        self._slider_volume: Optional[Slider] = None
        self._pre_mute_volume: float = 0.5
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

        # Main vertical content: logo + play + leaderboard
        root = BoxLayout(orientation="vertical", padding=40, spacing=14)

        title = Image(
            source="assets/menu_screen_logo.png",
            size_hint=(1, 0.6),
            allow_stretch=True,
            keep_ratio=True,
        )
        root.add_widget(title)

        self._btn_new_game = RoundedButton(
            text=f"[font=MaterialIcons]{_IC_PLAY}[/font]  {i18n.t('new_game')}",
            markup=True,
            font_size="20sp",
            size_hint=(0.5, 0.09),
            pos_hint={"center_x": 0.5},
            background_color=(0.9, 0.5, 0.1, 1),
        )
        self._btn_new_game.bind(on_release=self._handle_new_game)
        root.add_widget(self._btn_new_game)

        self._btn_leaderboard = RoundedButton(
            text=f"[font=MaterialIcons]{_IC_STAR}[/font]  {i18n.t('leaderboard')}",
            markup=True,
            font_size="20sp",
            size_hint=(0.5, 0.09),
            pos_hint={"center_x": 0.5},
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_leaderboard.bind(on_release=self._handle_leaderboard)
        root.add_widget(self._btn_leaderboard)

        self.add_widget(root)

        # Settings gear — top-right corner, transparent
        self._btn_settings = RoundedButton(
            text=_IC_GEAR,
            font_name="MaterialIcons",
            font_size="40sp",
            size_hint=(None, None),
            size=(_ICON_BTN_SIZE, _ICON_BTN_SIZE),
            pos_hint={"right": 0.98, "top": 0.98},
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=(0.75, 0.75, 0.75, 1),
        )
        self._btn_settings.bind(on_release=self._open_settings)
        self.add_widget(self._btn_settings)

        # Quit — bottom-left corner, transparent
        self._btn_quit = RoundedButton(
            text=_IC_QUIT,
            font_name="MaterialIcons",
            font_size="40sp",
            size_hint=(None, None),
            size=(_ICON_BTN_SIZE, _ICON_BTN_SIZE),
            pos_hint={"x": 0.02, "y": 0.02},
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=(0.75, 0.2, 0.2, 1),
        )
        self._btn_quit.bind(on_release=self._handle_quit)
        self.add_widget(self._btn_quit)

        self._build_settings_overlay()

    def _build_settings_overlay(self) -> None:
        dlg = DialogOverlay(title=i18n.t("settings"))

        self._lang_label = dlg.add_label(
            i18n.t("language") + ":",
            font_size="18sp",
            color=(0.8, 0.8, 0.8, 1),
        )

        lang_btn_row = BoxLayout(
            orientation="horizontal",
            size_hint=(0.85, None),
            height=_BUTTON_H,
            pos_hint={"center_x": 0.5},
            spacing=12,
        )
        self._btn_en = RoundedToggleButton(
            text="EN",
            group="language",
            state="down" if str(i18n.get('locale')) == "en" else "normal",
            font_size="16sp",
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_it = RoundedToggleButton(
            text="IT",
            group="language",
            state="down" if str(i18n.get('locale')) == "it" else "normal",
            font_size="16sp",
            background_color=(0.2, 0.5, 0.8, 1),
        )
        self._btn_en.bind(on_release=lambda _: self._set_language("en"))
        self._btn_it.bind(on_release=lambda _: self._set_language("it"))
        lang_btn_row.add_widget(self._btn_en)
        lang_btn_row.add_widget(self._btn_it)
        dlg.add_generic_widget(lang_btn_row, height=_BUTTON_H)

        if self._audio is not None:
            vol_row = BoxLayout(
                orientation="horizontal",
                size_hint=(0.85, None),
                height=_BUTTON_H,
                pos_hint={"center_x": 0.5},
                spacing=10,
            )
            init_icon = _IC_MUTE if self._audio.volume == 0.0 else _IC_VOL
            self._btn_volume = RoundedButton(
                text=init_icon,
                font_name="MaterialIcons",
                font_size="22sp",
                color=(0.8, 0.8, 0.8, 1),
                size_hint=(0.15, 1),
                background_normal="",
                background_down="",
                background_color=(0, 0, 0, 0),
            )
            self._btn_volume.bind(on_release=self._toggle_mute)
            vol_row.add_widget(self._btn_volume)
            self._slider_volume = Slider(
                min=0.0,
                max=1.0,
                value=self._audio.volume,
                size_hint=(0.85, 1),
                cursor_size=(20, 20),
            )
            self._slider_volume.bind(value=self._on_volume_change)
            vol_row.add_widget(self._slider_volume)
            dlg.add_generic_widget(vol_row, height=_BUTTON_H)

        dlg.add_button(
            text="Close",
            bg=(0.4, 0.4, 0.4, 1),
            on_release=self._close_settings,
        )

        self._settings_overlay = dlg

    def _open_settings(self, *_args: Any) -> None:
        if self._settings_overlay is not None:
            self.add_widget(self._settings_overlay)

    def _close_settings(self, *_args: Any) -> None:
        if self._settings_overlay is not None:
            self.remove_widget(self._settings_overlay)

    def _on_volume_change(self, _slider: Any, value: float) -> None:
        if self._audio is not None:
            self._audio.set_volume(value)
        if self._btn_volume is not None:
            self._btn_volume.text = _IC_MUTE if value == 0.0 else _IC_VOL

    def _toggle_mute(self, *_args: Any) -> None:
        if self._audio is None or self._slider_volume is None:
            return
        if self._audio.volume > 0.0:
            self._pre_mute_volume = self._audio.volume
            self._slider_volume.value = 0.0
        else:
            self._slider_volume.value = self._pre_mute_volume if self._pre_mute_volume > 0.0 else 0.5

    def _handle_quit(self, *_args: Any) -> None:
        App.get_running_app().stop()

    def _update_bg(self, *_args: Any) -> None:
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _handle_new_game(self, *_args: Any) -> None:
        if self._on_new_game is not None:
            self._on_new_game()

    def _handle_leaderboard(self, *_args: Any) -> None:
        if self._on_leaderboard is not None:
            self._on_leaderboard()

    def _set_language(self, lang: str) -> None:
        i18n.set('locale', lang)
        self._refresh_labels()

    def _refresh_labels(self) -> None:
        self._btn_new_game.text = f"[font=MaterialIcons]{_IC_PLAY}[/font]  {i18n.t('new_game')}"
        self._btn_leaderboard.text = f"[font=MaterialIcons]{_IC_STAR}[/font]  {i18n.t('leaderboard')}"
        self._lang_label.text = i18n.t("language") + ":"
