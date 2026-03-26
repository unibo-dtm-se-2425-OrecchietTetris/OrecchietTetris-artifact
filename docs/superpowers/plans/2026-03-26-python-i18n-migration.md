# python-i18n Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the custom `I18n` class with direct use of the `python-i18n` library API.

**Architecture:** Translation strings move to YAML locale files loaded by `python-i18n`. The library is configured once in `TetrisApp.build()`. All view files call `i18n.t('key')` / `i18n.set('locale', lang)` / `i18n.get('locale')` directly — no wrapper class, no injected instance.

**Tech Stack:** Python 3.11+, python-i18n ^0.3.9 (already a declared dependency), PyYAML (pulled in by python-i18n), Kivy, mypy strict, flake8, pytest.

---

## File Map

| Action | Path |
|--------|------|
| Create | `OrecchietTetris/view/locales/en.yml` |
| Create | `OrecchietTetris/view/locales/it.yml` |
| Modify | `OrecchietTetris/view/app.py` |
| Modify | `OrecchietTetris/view/menu_screen.py` |
| Modify | `OrecchietTetris/view/game_screen.py` |
| Delete | `OrecchietTetris/view/i18n.py` |
| Modify | `OrecchietTetris/view/__init__.py` |
| Delete | `tests/view/test_i18n.py` |

---

## Task 1: Create locale YAML files

**Files:**
- Create: `OrecchietTetris/view/locales/en.yml`
- Create: `OrecchietTetris/view/locales/it.yml`

`python-i18n` expects locale files named `{locale}.{format}` when configured with
`filename_format = '{locale}.{format}'`. Each file must have a top-level key matching
the locale code, with translation key/value pairs nested under it.

- [ ] **Step 1: Create `en.yml`**

```yaml
en:
  new_game: "New Game"
  language: "Language"
  pause: "Pause"
  resume: "Resume"
  game_over: "Game Over"
  score: "Score"
  level: "Level"
  lines: "Lines"
  hold: "Hold"
  next: "Next"
  back_to_menu: "Back to Menu"
```

- [ ] **Step 2: Create `it.yml`**

```yaml
it:
  new_game: "Nuova Partita"
  language: "Lingua"
  pause: "Pausa"
  resume: "Riprendi"
  game_over: "Partita Finita"
  score: "Punteggio"
  level: "Livello"
  lines: "Righe"
  hold: "Tieni"
  next: "Prossimo"
  back_to_menu: "Menu Principale"
```

- [ ] **Step 3: Verify YAML is valid**

```bash
python -c "import yaml; yaml.safe_load(open('OrecchietTetris/view/locales/en.yml')); yaml.safe_load(open('OrecchietTetris/view/locales/it.yml')); print('OK')"
```

Expected output: `OK`

- [ ] **Step 4: Commit**

```bash
git add OrecchietTetris/view/locales/en.yml OrecchietTetris/view/locales/it.yml
git commit -m "feat(i18n): add python-i18n locale YAML files (en, it)"
```

---

## Task 2: Update `app.py`

**Files:**
- Modify: `OrecchietTetris/view/app.py`

Replace `I18n("en")` instantiation with a one-time `python-i18n` configuration block.
Remove `i18n=self._i18n` from both screen constructors. The `pathlib.Path` import is needed
to build the locale directory path robustly regardless of working directory.

- [ ] **Step 1: Replace contents of `app.py`**

```python
from __future__ import annotations

from pathlib import Path

import i18n  # type: ignore[import-untyped]
from kivy.app import App  # type: ignore[import-untyped]
from kivy.uix.screenmanager import ScreenManager, NoTransition  # type: ignore[import-untyped]

from OrecchietTetris.model import Tetris
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

    def build(self) -> ScreenManager:
        i18n.set('file_format', 'yml')
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('load_path', [str(Path(__file__).parent / 'locales')])
        i18n.set('locale', 'en')
        i18n.set('fallback', 'en')

        self._model = Tetris()

        self._sm = ScreenManager(transition=NoTransition())

        self._menu = MenuScreen(
            on_new_game=self._start_game,
            name="menu",
        )
        self._game = GameScreen(
            model=self._model,
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
```

- [ ] **Step 2: Run type check**

```bash
poetry run poe mypy
```

Expected: no new errors in `app.py`. (Other files still import `I18n` so they may show
errors — those are fixed in subsequent tasks.)

- [ ] **Step 3: Commit**

```bash
git add OrecchietTetris/view/app.py
git commit -m "feat(i18n): configure python-i18n in TetrisApp, remove I18n instance"
```

---

## Task 3: Update `menu_screen.py`

**Files:**
- Modify: `OrecchietTetris/view/menu_screen.py`

Remove the `I18n` import and `i18n: I18n` constructor parameter. Use the `i18n` module
directly. `i18n.get('locale')` returns `Any`, so cast to `str` to satisfy mypy strict.

- [ ] **Step 1: Replace contents of `menu_screen.py`**

```python
from __future__ import annotations

from typing import Any, Callable, Optional

import i18n  # type: ignore[import-untyped]
from kivy.uix.screenmanager import Screen  # type: ignore[import-untyped]
from kivy.uix.boxlayout import BoxLayout  # type: ignore[import-untyped]
from kivy.uix.button import Button  # type: ignore[import-untyped]
from kivy.uix.label import Label  # type: ignore[import-untyped]
from kivy.uix.togglebutton import ToggleButton  # type: ignore[import-untyped]
from kivy.graphics import Color, Rectangle  # type: ignore[import-untyped]

from OrecchietTetris.utils import EventType
from OrecchietTetris.view.interfaces import IView


class MenuScreen(Screen, IView):
    """Main menu screen.

    Shows a *New Game* button and a language toggle (EN / IT).
    All text is sourced from ``python-i18n`` so switching the language
    refreshes labels immediately.

    Parameters
    ----------
    on_new_game:
        Called (no arguments) when the player presses *New Game*.
    """

    def __init__(
        self,
        on_new_game: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
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
            text=i18n.t("new_game"),
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

        self.add_widget(root)

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
        self._btn_new_game.text = i18n.t("new_game")
        self._lang_label.text = i18n.t("language") + ":"
```

- [ ] **Step 2: Run type check**

```bash
poetry run poe mypy
```

Expected: no errors in `menu_screen.py`.

- [ ] **Step 3: Commit**

```bash
git add OrecchietTetris/view/menu_screen.py
git commit -m "feat(i18n): migrate MenuScreen to python-i18n direct API"
```

---

## Task 4: Update `game_screen.py`

**Files:**
- Modify: `OrecchietTetris/view/game_screen.py`

Remove the `I18n` import and `i18n: I18n` constructor parameter. Replace every
`self._i18n.t("key")` with `i18n.t("key")`. The `self._i18n` field is also removed.

- [ ] **Step 1: Remove `I18n` import (line 18) and add `i18n` import**

Replace:
```python
from OrecchietTetris.view.i18n import I18n
```
With:
```python
import i18n  # type: ignore[import-untyped]
```

- [ ] **Step 2: Remove `i18n: I18n` parameter and `self._i18n` assignment**

Replace the constructor signature and body (lines 145–161):
```python
    def __init__(
        self,
        model: ITetris,
        on_back_to_menu: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._model = model
        self._on_back_to_menu = on_back_to_menu
        self._renderer = BlockRenderer()
        self._keyboard: Any = None
        self._overlay: Optional[Widget] = None

        self._board_cells: list[list[_Cell]] = []
        self._build_ui()
```

Also update the docstring — replace:
```
    i18n:
        Shared localization instance.
```
with nothing (remove those two lines).

- [ ] **Step 3: Replace all `self._i18n.t(...)` calls**

There are 14 occurrences. Replace every instance of `self._i18n.t(` with `i18n.t(` across the file.

Run to verify zero occurrences remain:
```bash
grep -n "self._i18n" OrecchietTetris/view/game_screen.py
```
Expected: no output.

- [ ] **Step 4: Run type check**

```bash
poetry run poe mypy
```

Expected: no errors in `game_screen.py`.

- [ ] **Step 5: Commit**

```bash
git add OrecchietTetris/view/game_screen.py
git commit -m "feat(i18n): migrate GameScreen to python-i18n direct API"
```

---

## Task 5: Delete `i18n.py`, `test_i18n.py`, update `__init__.py`

**Files:**
- Delete: `OrecchietTetris/view/i18n.py`
- Delete: `tests/view/test_i18n.py`
- Modify: `OrecchietTetris/view/__init__.py`

All consumers have been migrated, so the custom wrapper and its tests can be removed.

- [ ] **Step 1: Delete `i18n.py` and `test_i18n.py`**

```bash
rm OrecchietTetris/view/i18n.py
rm tests/view/test_i18n.py
```

- [ ] **Step 2: Update `__init__.py`**

Replace the entire file with:
```python
from .interfaces import IView

__all__ = ["IView"]
```

- [ ] **Step 3: Run full checks**

```bash
poetry run poe mypy
poetry run poe flake8
poetry run poe test
```

Expected:
- `mypy`: no errors
- `flake8`: no errors
- `pytest`: all tests pass (the removed `test_i18n.py` tests are gone; all other tests pass)

- [ ] **Step 4: Commit**

```bash
git add -u OrecchietTetris/view/__init__.py OrecchietTetris/view/i18n.py tests/view/test_i18n.py
git commit -m "feat(i18n): remove custom I18n class and i18n tests"
```
