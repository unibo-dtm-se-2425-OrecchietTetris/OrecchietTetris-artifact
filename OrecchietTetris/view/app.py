from __future__ import annotations

from kivy.app import App  # type: ignore[import]
from kivy.uix.screenmanager import ScreenManager, NoTransition  # type: ignore[import]

from OrecchietTetris.model import Tetris
from OrecchietTetris.view.i18n import I18n
from OrecchietTetris.view.menu_screen import MenuScreen
from OrecchietTetris.view.game_screen import GameScreen


class TetrisApp(App):
    """Kivy application entry point.

    Screen flow
    -----------
    * Starts on **MenuScreen**.
    * Pressing *New Game* switches to **GameScreen** and calls ``model.play()``.
    * On game over or when the player presses *Back to Menu* the app returns to
      **MenuScreen** and stops the model loop.
    """

    def build(self) -> ScreenManager:  # type: ignore[override]
        self._i18n = I18n("en")
        self._model = Tetris()

        self._sm = ScreenManager(transition=NoTransition())

        self._menu = MenuScreen(
            i18n=self._i18n,
            on_new_game=self._start_game,
            name="menu",
        )
        self._game = GameScreen(
            model=self._model,
            i18n=self._i18n,
            on_back_to_menu=self._back_to_menu,
            name="game",
        )

        self._sm.add_widget(self._menu)
        self._sm.add_widget(self._game)
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
        self._model.play()

    def _back_to_menu(self) -> None:
        """Stop the game loop and return to the main menu."""
        self._model.stop()
        self._game.hide()
        self._menu.show()
        self._sm.current = "menu"
