# OrecchietTetris

An exact copy of the Tetris game, with Apulian elements. Built as a Software Engineering university project.

## Features

- Classic Tetris gameplay with all 7 standard tetrominoes (I, O, T, S, Z, J, L)
- Tetromino rotation, hard drop, and shadow piece (ghost piece preview)
- Hold slot — store the current piece and swap it back in at any time
- Kivy-based GUI with Italian / English language switching
- Observer pattern architecture decoupling game logic from the view
- Formal interfaces (`ITetromino`, `IBoard`, `ITetris`, `IView`) for clean dependency inversion
- Automated testing via GitHub Actions (Windows, macOS, Ubuntu)
- Automatic releases to [PyPI](https://pypi.org/) via [semantic-release](https://semantic-release.gitbook.io) on pushes to `master`
- Automatic dependency updates via [Renovate](https://docs.renovatebot.com/)

## Requirements

- Python >= 3.11
- [Kivy](https://kivy.org/) >= 2.3 (installed automatically by Poetry)
- Node >= 25 and npm >= 11.11 (for semantic-release)
- [Poetry](https://python-poetry.org/) (dependency manager)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact
    cd OrecchietTetris-artifact
    ```

2. Install Poetry if you don't have it yet:
    ```bash
    pip install -r requirements.txt
    ```

3. Install the project's dependencies:
    ```bash
    poetry install
    npm install
    ```

4. (Optional) Install pre-commit hooks for commit-message linting:
    ```bash
    poetry run poe hooks
    ```

## Usage

Run the game:
```bash
poetry run OrecchietTetris
```

or alternatively:
```bash
python -m OrecchietTetris
```

## Development

### Run tests
```bash
poetry run poe test
```

Run a single test file or test case:
```bash
poetry run pytest -v tests/model/test_tetromino.py
poetry run pytest -v tests/model/test_tetromino.py::test_rotations
```

### Coverage
```bash
poetry run poe coverage
```

### Lint & type check
```bash
poetry run poe flake8
poetry run poe mypy
```

## Project structure

```
OrecchietTetris-artifact/
├── OrecchietTetris/
│   ├── model/
│   │   ├── interfaces/
│   │   │   ├── itetromino.py   # ITetromino abstract interface
│   │   │   ├── iboard.py       # IBoard abstract interface
│   │   │   └── itetris.py      # ITetris(Subject) abstract interface
│   │   ├── tetromino.py        # ShapeType enum and Tetromino(ITetromino)
│   │   ├── board.py            # Board(IBoard) — stub
│   │   └── tetris.py           # Tetris(ITetris) — stub
│   ├── view/
│   │   ├── interfaces/
│   │   │   └── i_view.py       # IView(Observer) abstract interface
│   │   ├── i18n.py             # I18n — EN/IT runtime localization
│   │   ├── block_renderer.py   # BlockRenderer — int → RGBA / Image
│   │   ├── menu_screen.py      # MenuScreen(IView) — Kivy main menu
│   │   ├── game_screen.py      # GameScreen(IView) — Kivy game board
│   │   └── app.py              # TetrisApp(App) — Kivy entry point
│   ├── gui/
│   │   └── TetrisGui.py        # Legacy stub (Observer)
│   ├── utils/
│   │   └── observer_subject.py # Subject, Observer, EventType
│   ├── __init__.py
│   └── __main__.py
├── tests/
│   ├── model/
│   │   └── test_tetromino.py
│   └── view/
│       ├── test_i18n.py
│       ├── test_block_renderer.py
│       └── test_i_view.py
├── assets/
│   └── blocks/                 # I.png … L.png  (block textures)
├── pyproject.toml
└── README.md
```

## Architecture

The project uses the **Observer pattern** to decouple game logic from the view, with **abstract interfaces** for dependency inversion.

### Components

| Component | Role |
|---|---|
| `Tetromino(ITetromino)` | Falling piece with clockwise rotation |
| `Board(IBoard)` | Pure grid engine — collision, locking, line clearing |
| `Tetris(ITetris)` | Game orchestrator; fires `EventType` events on every state change |
| `MenuScreen(IView)` | Kivy main menu with language selector |
| `GameScreen(IView)` | Kivy 10×20 board, previews, score, keyboard input |
| `TetrisApp(App)` | Kivy application; manages screen transitions |
| `I18n` | Runtime EN/IT string lookup |
| `BlockRenderer` | Maps piece integers to RGBA colours and image paths |

### Observer events (`EventType` enum)

| Event | When | Data |
|---|---|---|
| `BOARD_UPDATED` | piece moved, rotated, or locked | `None` |
| `NEW_PIECE` | new piece spawned | `ITetromino` |
| `HOLD_UPDATED` | hold slot changed | `ITetromino \| None` |
| `LINES_CLEARED` | lines removed | `int` |
| `SCORE_UPDATED` | score changed | `int` |
| `GAME_OVER` | spawn blocked | `None` |
| `PAUSED` / `RESUMED` | pause toggled | `None` |

### Keyboard controls

| Key | Action |
|---|---|
| ← / → | Move left / right |
| ↓ | Soft drop |
| ↑ or X | Rotate clockwise |
| Space | Hard drop |
| C | Hold |
| P or Escape | Pause / Resume |

## Releases

Releases are automated via GitHub Actions when pushing to `master`. Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for `semantic-release` to compute version numbers correctly (e.g. `feat:`, `fix:`, `chore:`).

## License

[Apache 2.0](LICENSE)
