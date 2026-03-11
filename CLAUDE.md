# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

An exact copy of the Tetris game, with Apulian elements. Built as a Software Engineering university project. It is a Python package managed with Poetry, using pytest for testing, mypy for type checking, and flake8 for linting.

## Commands

### Setup
```bash
pip install -r requirements.txt   # install Poetry
poetry install                    # install all dependencies
npm install                       # install semantic-release and commitlint (for releases)
poetry run poe hooks              # install pre-commit hooks (commit-msg linting)
```

### Testing
```bash
poetry run poe test               # run all tests
poetry run pytest -v tests/model/test_tetromino.py  # run a single test file
poetry run pytest -v tests/model/test_tetromino.py::test_rotations  # run a single test
poetry run poe coverage           # run tests with coverage report
```

### Linting & type checking
```bash
poetry run poe flake8             # lint
poetry run poe mypy               # type check
poetry run poe compile            # compile check
```

### Run the app
```bash
poetry run OrecchietTetris        # run via script entry point
python -m OrecchietTetris         # run as module
```

## Architecture

The project follows a Model-View (Observer pattern) architecture with abstract interfaces for dependency inversion.

- **`OrecchietTetris/model/`** — game logic
  - `interfaces/` — abstract base classes split into separate files:
    - `itetromino.py`: `ITetromino` — `shape_type` (str), `shape` (2D list), `rotate()`
    - `iboard.py`: `IBoard` — `rows`, `cols`, `grid`, `is_valid_position()`, `place_tetromino()`, `clear_lines()`, `is_game_over()`, `reset()`
    - `itetris.py`: `ITetris(Subject, ABC)` — full game orchestrator contract; board/piece state, score/level, game-flow actions (`start`, `pause`, `resume`, `tick`), player actions (`move_left`, `move_right`, `move_down`, `rotate`, `hard_drop`, `hold`), automatic loop (`play`/`stop`).
  - `tetromino.py`: `ShapeType` enum (I, O, T, S, Z, J, L shapes as numbered 2D tuples, e.g. `I_SHAPE = ((1, 1, 1, 1),)`) and `Tetromino(ITetromino)` with `rotate()` (transpose/reverse).
  - `board.py`: `Board(IBoard)` — **stub, not yet implemented**.
  - `tetris.py`: `Tetris(ITetris)` — **stub, not yet implemented**.

- **`OrecchietTetris/utils/`** — shared utilities
  - `observer_subject.py`: `Subject`, `Observer` base classes, and `EventType` enum. `Subject.notify(event_type, data)` calls `observer.update(event_type, data)` on all attached observers. `EventType` values: `BOARD_UPDATED`, `NEW_PIECE`, `LINES_CLEARED`, `SCORE_UPDATED`, `GAME_OVER`, `PAUSED`, `RESUMED`, `HOLD_UPDATED`.

- **`OrecchietTetris/gui/`** — view layer
  - `TetrisGui(Observer)`: **stub, not yet implemented**. Will react to `EventType` events from `Tetris`.

### Implementation status
- **Fully implemented:** `Tetromino` (shapes + rotation), all interface definitions, observer infrastructure (`Subject`, `Observer`, `EventType`), CI/CD pipeline, linting/type-checking config.
- **Stubs (not yet implemented):** `Board`, `Tetris`, `TetrisGui`, `main()` entry point.

### Import hierarchy (no circular dependencies)
```
utils/observer_subject.py  ←  model/interfaces/  ←  model/tetromino.py  ←  model/board.py  ←  model/tetris.py
                                                                                                      ↓
                                                                                              gui/TetrisGui.py
```

## Conventions

- All public APIs must be fully type-annotated (mypy strict mode is enforced).
- Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — `semantic-release` uses them to compute version numbers and publish to PyPI automatically on pushes to `master`.
- Tests live in `tests/` mirroring the package structure (e.g., `tests/model/` for `OrecchietTetris/model/`).
- Max line length: 120 characters (flake8).
- Node.js >= 25 required for npm tooling.
