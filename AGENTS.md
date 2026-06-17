# AGENTS.md

AI-agent-oriented guide for **OrecchietTetris** — a Tetris clone with Apulian theming, built as a Software Engineering university project. Python package managed with Poetry, Kivy GUI, Observer pattern architecture.

---

## Project overview

- **Language:** Python 3.11+
- **GUI:** Kivy 2.3+
- **Package manager:** Poetry
- **Test framework:** pytest
- **Type checker:** mypy (strict mode)
- **Linter:** flake8 (max line length: 120)
- **Release automation:** semantic-release (Node.js ≥ 25, npm ≥ 11.11)
- **Architecture:** Model-View with Observer pattern and abstract interfaces for dependency inversion

The game board is 10×20. Seven tetromino types (I, O, T, S, Z, J, L), each mapped to an Apulian food image. EN/IT localization at runtime.

All layers are fully implemented: `Tetromino`, `Board`, `Tetris`, all interfaces, observer infrastructure, complete Kivy view (`MenuScreen`, `GameScreen`, `TetrisApp`), `I18n`, `BlockRenderer`, `main()` entry point, CI/CD pipeline.

---

## Setup commands

```bash
pip install -r requirements.txt   # install Poetry
poetry install                    # install all dependencies + creates .venv/
npm install                       # install semantic-release and commitlint (Node.js >= 25 required)
poetry run poe hooks              # install pre-commit hooks (commit-msg linting)
```

---

## Run commands

```bash
poetry run OrecchietTetris   # via script entry point
python -m OrecchietTetris    # via module
```

---

## Test commands

```bash
poetry run poe test                                                        # all tests
poetry run pytest -v tests/model/test_tetromino.py                        # single file
poetry run pytest -v tests/model/test_tetromino.py::test_rotations        # single test
poetry run poe coverage                                                    # coverage report
```

Always run `poetry run poe test` before considering any task complete.

---

## Lint and type check commands

```bash
poetry run poe flake8    # lint (max line length: 120)
poetry run poe mypy      # type check (strict mode)
poetry run poe compile   # compile check
```

Run all three after every change. All must pass with zero errors.

---

## Architecture

```
utils/observer_subject.py  ←  model/interfaces/  ←  model/tetromino.py  ←  model/board.py  ←  model/tetris.py
         ↓                           ↓
  view/interfaces/i_view.py    view/i18n.py
         ↓
  view/block_renderer.py
         ↓
  view/menu_screen.py  view/game_screen.py
         ↓
  view/app.py
```

No circular imports. Lower layers never import from higher layers. Never break this hierarchy.

### Key modules and APIs

**`OrecchietTetris/utils/observer_subject.py`**

- `Subject` — base class for observable objects. `notify(event_type, data)` calls `observer.update(event_type, data)` on every attached observer.
- `Observer` — base class; implement `update(event_type, data)`.
- `EventType` enum — `BOARD_UPDATED`, `NEW_PIECE`, `LINES_CLEARED`, `SCORE_UPDATED`, `GAME_OVER`, `PAUSED`, `RESUMED`, `HOLD_UPDATED`.

**`OrecchietTetris/model/interfaces/`** — abstract base classes, one file per interface:

- `itetromino.py` → `ITetromino`: properties `shape_type` (str), `shape` (2D list); method `rotate()`.
- `iboard.py` → `IBoard`: properties `rows`, `cols`, `grid`; methods `is_valid_position()`, `place_tetromino()`, `clear_lines()`, `is_game_over()`, `reset()`.
- `itetris.py` → `ITetris(Subject, ABC)`: full orchestrator contract — board/piece state, score/level, game-flow actions (`start`, `pause`, `resume`, `tick`), player actions (`move_left`, `move_right`, `move_down`, `rotate`, `hard_drop`, `hold`), loop control (`play`, `stop`).

**`OrecchietTetris/model/tetromino.py`**

- `ShapeType` enum — I, O, T, S, Z, J, L shapes as 2D tuples of ints (1 = filled, 0 = empty). Example: `I_SHAPE = ((1, 1, 1, 1),)`.
- `Tetromino(ITetromino)` — `rotate()` does transpose + reverse (clockwise).

**`OrecchietTetris/model/board.py`**

- `Board(IBoard)` — manages the fixed grid and the falling piece.
- `clear_lines()` returns `list[int]` — original row indices of cleared rows, sorted descending (bottom-first). Used by the view to animate clearing.

**`OrecchietTetris/model/tetris.py`**

- `Tetris(ITetris)` — main game orchestrator.
- `_lock_piece()` — calls `clear_lines()`, updates score/level with `len(cleared)`, notifies `LINES_CLEARED` with the row-index list.
- `_spawn_piece(piece: ITetromino | None = None)` — also accepts an `ITetromino` argument; used by `hold()` to swap back a held piece.
- `play()` / `stop()` — manage a daemon thread running `tick()` on `tick_interval`.

**`OrecchietTetris/view/interfaces/i_view.py`**

- `IView(Observer, ABC)` — `show()`, `hide()`, `update(event_type, data)`.

**`OrecchietTetris/view/i18n.py`**

- `I18n` — runtime EN/IT localization. `t(key)` returns translated string; `set_language(lang)` switches at runtime.

**`OrecchietTetris/view/block_renderer.py`**

- `BlockRenderer` — maps cell integers (0–7) to RGBA tuples and image paths.
- `BLOCK_IMAGES` maps 1–7 → `assets/blocks/<X>.png`.

**`OrecchietTetris/view/menu_screen.py`**

- `MenuScreen(Screen, IView)` — New Game button + EN/IT language toggle.

**`OrecchietTetris/view/game_screen.py`**

- `GameScreen(Screen, IView)` — 10×20 board, falling piece, ghost/shadow, next/hold previews, score/level/lines panel, pause button, game-over overlay, keyboard input.

**`OrecchietTetris/view/app.py`**

- `TetrisApp(App)` — Kivy app; starts on `MenuScreen`, transitions to `GameScreen` on New Game, returns on game-over or back-to-menu.

**`OrecchietTetris/gui/`** — legacy stub, superseded by `view/`. Do not extend.

---

## Observer event contracts

Non-obvious data payloads in `Subject.notify(event_type, data)`:

| `EventType` | Fired when | `data` payload |
|-------------|------------|----------------|
| `BOARD_UPDATED` | piece moved, rotated, or locked | `None` |
| `NEW_PIECE` | new piece spawned | `ITetromino` — the piece now current (after spawn) |
| `HOLD_UPDATED` | hold slot changed | `ITetromino \| None` — the piece now in the hold slot |
| `LINES_CLEARED` | lines removed | `list[int]` — cleared row indices sorted descending (bottom-first) |
| `SCORE_UPDATED` | score changed | `int` |
| `GAME_OVER` | spawn blocked | `None` |
| `PAUSED` / `RESUMED` | pause toggled | `None` |

`GameScreen` animates `LINES_CLEARED` rows white one-by-one and suppresses `BOARD_UPDATED` redraws during animation via `_clearing_animation: bool`.

---

## Keyboard controls (GameScreen)

| Key | Action |
| --- | --- |
| ← / → | `move_left()` / `move_right()` |
| ↓ | `move_down()` (soft drop) |
| ↑ or X | `rotate()` (clockwise) |
| Space | `hard_drop()` |
| C | `hold()` |
| P or Escape | `pause()` / `resume()` |
| Q | Quit |
| M | Toggle music |
| N | Next track |
| B | Previous track |

---

## Code style guidelines

- **Type annotations required** on all public APIs. mypy strict mode is enforced — no `Any`, no missing return types.
- **Max line length:** 120 characters.
- **No comments** unless the WHY is non-obvious (hidden constraint, subtle invariant, workaround). Never describe what the code does.
- **No circular imports.** Respect the import hierarchy above.
- **Interfaces live in `model/interfaces/`** as separate files per interface. Implementations depend on interfaces, never on concrete siblings.
- **Tests mirror package structure:** `tests/model/` for `OrecchietTetris/model/`, etc.
- **Do not add features or abstractions** beyond what the task requires.
- **Do not add error handling** for scenarios that cannot happen — trust internal invariants.

---

## Testing instructions

- Tests live in `tests/`, mirroring the package structure.
- Test model logic (tetromino, board, game orchestrator) with unit tests — no Kivy dependency in model tests.
- Do not mock the model layer when testing view integration; test against real model instances where possible.
- Use `poetry run poe coverage` to verify coverage after adding new functionality.

---

## Commit message guidelines

Commits **must** follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). `semantic-release` reads these to compute version numbers and publish to PyPI automatically on pushes to `master`.

```
<type>(<optional scope>): <short description>

[optional body]

[optional footer]
```

### Valid types

| Type | Use for |
|------|---------|
| `feat` | New user-facing feature (triggers minor version bump) |
| `fix` | Bug fix (triggers patch version bump) |
| `docs` | Documentation only |
| `refactor` | Code change with no behavior change |
| `test` | Adding or correcting tests |
| `chore` | Build, deps, tooling, CI |
| `style` | Formatting, whitespace |
| `perf` | Performance improvement |

A `BREAKING CHANGE:` footer or `!` after the type (e.g. `feat!:`) triggers a major version bump.

### Examples

```
feat(board): add T-spin detection
fix(tetris): prevent double-lock on hard drop at spawn row
refactor(view): extract ghost piece drawing to helper method
test(board): add edge cases for clear_lines with full grid
chore(deps): upgrade kivy to 2.3.1
docs: update architecture section in README
```

---

## Dev environment tips

- All commands assume the Poetry virtualenv is active (`poetry run <cmd>`) or that `.venv` is activated in the shell.
- Kivy requires a display. GUI tests or manual runs will fail in headless CI without a virtual display (e.g. `Xvfb`).
- `play()` / `stop()` on `Tetris` manage a daemon thread running `tick()` on `tick_interval`. In tests, drive `tick()` manually instead of calling `play()` to avoid timing dependencies.
- `Board.clear_lines()` returns `list[int]` (original row indices of cleared rows, sorted descending). Use the length for scoring, the indices for animation.
- `ShapeType` shapes are tuples of tuples of ints (1 = filled). `Tetromino.rotate()` does transpose + reverse for clockwise rotation.
- `_spawn_piece()` accepts an optional `ITetromino` argument — pass the held piece to swap it back in without drawing from the bag.
