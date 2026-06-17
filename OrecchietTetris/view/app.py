from __future__ import annotations

import i18n  # type: ignore[import-untyped]
from kivy.app import App  # type: ignore[import-untyped]
from kivy.core.text import LabelBase  # type: ignore[import-untyped]
from kivy.uix.screenmanager import ScreenManager, NoTransition  # type: ignore[import-untyped]

from OrecchietTetris.utils.paths import ASSETS_DIR, LOCALES_DIR
from OrecchietTetris.model import Tetris
from OrecchietTetris.leaderboard.csv_leaderboard_repository import CsvLeaderboardRepository
from OrecchietTetris.audio.kivy_audio_controller import KivyAudioController
from OrecchietTetris.view.menu_screen import MenuScreen
from OrecchietTetris.view.game_screen import GameScreen
from OrecchietTetris.view.leaderboard_screen import LeaderboardScreen


class TetrisApp(App):
    """Kivy application entry point.

    Screen flow
    -----------
    * Starts on **MenuScreen**.
    * Pressing *New Game* switches to **GameScreen** and calls ``game.begin()``.
    * Pressing *Leaderboard* switches to **LeaderboardScreen**.
    * On game over or when the player presses *Back to Menu* the app returns to
      **MenuScreen** and ends the game-screen tick loop.
    """

    title = "OrecchietTetris"
    icon = str(ASSETS_DIR / "app_icon.webp")

    def build(self) -> ScreenManager:
        LabelBase.register(
            name="MaterialIcons",
            fn_regular=str(ASSETS_DIR / "fonts" / "MaterialIcons-Regular.ttf"),
        )

        i18n.set('file_format', 'yml')
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('load_path', [str(LOCALES_DIR)])
        i18n.set('locale', 'en')
        i18n.set('fallback', 'en')

        self._model = Tetris()
        self._leaderboard_repo = CsvLeaderboardRepository()
        self._audio = KivyAudioController()
        self._audio.play()

        self._sm = ScreenManager(transition=NoTransition())

        self._menu = MenuScreen(
            on_new_game=self._start_game,
            on_leaderboard=self._show_leaderboard,
            audio=self._audio,
            name="menu",
        )
        self._game = GameScreen(
            model=self._model,
            audio=self._audio,
            repository=self._leaderboard_repo,
            on_back_to_menu=self._back_to_menu,
            on_name_saved=self._on_name_saved,
            name="game",
        )
        self._leaderboard = LeaderboardScreen(
            repository=self._leaderboard_repo,
            on_back=self._back_to_menu_from_leaderboard,
            name="leaderboard",
        )

        self._sm.add_widget(self._menu)
        self._sm.add_widget(self._game)
        self._sm.add_widget(self._leaderboard)
        self._sm.current = "menu"
        return self._sm

    # ------------------------------------------------------------------
    # Screen transitions
    # ------------------------------------------------------------------

    def _start_game(self) -> None:
        """Switch to the game screen and begin a new game."""
        self._game.show()
        self._menu.hide()
        self._sm.current = "game"
        self._game.begin()

    def _back_to_menu(self) -> None:
        """Stop the game loop and return to the main menu."""
        self._game.end()
        self._game.hide()
        self._menu.show()
        self._sm.current = "menu"

    def _show_leaderboard(self) -> None:
        """Switch to the leaderboard screen."""
        self._leaderboard.show()
        self._menu.hide()
        self._sm.current = "leaderboard"

    def _back_to_menu_from_leaderboard(self) -> None:
        """Return to the main menu from the leaderboard screen."""
        self._leaderboard.hide()
        self._menu.show()
        self._sm.current = "menu"

    def _on_name_saved(self, name: str) -> None:
        """Forward the saved player name to the leaderboard for highlighting."""
        self._leaderboard.set_current_player(name)
