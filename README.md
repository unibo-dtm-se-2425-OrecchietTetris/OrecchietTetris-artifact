# OrecchietTetris

An exact copy of the Tetris game, with Apulian elements. Built as a Software Engineering university project.

## Features

- Classic Tetris gameplay with all 7 standard tetrominoes (I, O, T, S, Z, J, L)
- Tetromino rotation, hard drop, and shadow piece (ghost piece preview)
- Hold slot — store the current piece and swap it back in at any time
- Observer pattern architecture decoupling game logic from the GUI
- Formal interfaces (`ITetromino`, `IBoard`, `ITetris`) for clean dependency inversion
- Automated testing via GitHub Actions (Windows, macOS, Ubuntu)
- Automatic releases to [PyPI](https://pypi.org/) via [semantic-release](https://semantic-release.gitbook.io) on pushes to `master`
- Automatic dependency updates via [Renovate](https://docs.renovatebot.com/)

## Requirements

- Python >= 3.11
- Node >= 20 and npm >= 10.8 (for semantic-release)
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
│   │   ├── interfaces.py       # ITetromino, IBoard, ITetris abstract interfaces
│   │   ├── tetromino.py        # ShapeType enum and Tetromino(ITetromino)
│   │   ├── board.py            # Board(IBoard) — fixed grid engine
│   │   └── tetris.py           # Tetris(Subject, ITetris) — game orchestrator
│   ├── gui/
│   │   └── TetrisGui.py        # GUI layer (Observer)
│   ├── utils/
│   │   └── observer_subject.py # Observer pattern base classes
│   ├── __init__.py
│   └── __main__.py
├── tests/
│   └── model/
│       └── test_tetromino.py
├── pyproject.toml
└── README.md
```

## Architecture

The project uses the **Observer pattern** to decouple game logic from the view, with **abstract interfaces** for dependency inversion:

- `ITetromino`, `IBoard`, `ITetris` — abstract interfaces defined in `model/interfaces.py`; `ITetris` inherits from `Subject` so the observer contract is part of the interface itself
- `Tetris(ITetris)` — game orchestrator; fires observer events on every state change
- `TetrisGui(Observer)` — reacts to game events via `update(event_type, data)`
- `Board(IBoard)` — pure grid engine (collision detection, line clearing)
- `Tetromino(ITetromino)` — falling piece with clockwise rotation

### Observer events fired by `Tetris`

| Event | When | Data |
|---|---|---|
| `board_updated` | piece moved, rotated, or locked | `None` |
| `new_piece` | new piece spawned | `ITetromino` |
| `hold_updated` | hold slot changed | `ITetromino \| None` |
| `lines_cleared` | lines removed | `int` |
| `score_updated` | score changed | `int` |
| `game_over` | spawn blocked | `None` |
| `paused` / `resumed` | pause toggled | `None` |

## Releases

Releases are automated via GitHub Actions when pushing to `master`. Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for `semantic-release` to compute version numbers correctly (e.g. `feat:`, `fix:`, `chore:`).

## License

[Apache 2.0](LICENSE)
