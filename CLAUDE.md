# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

An exact copy of the Tetris game, with Apulian elements. Built as a Software Engineering university project. It is a Python package managed with Poetry, using pytest for testing, mypy for type checking, and flake8 for linting.

## Commands

### Setup
```bash
pip install -r requirements.txt   # install Poetry
poetry install                    # install all dependencies
npm install                       # install semantic-release globally (for releases)
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
  - `interfaces.py`: `ITetromino`, `IBoard`, `ITetris` — abstract base classes. `ITetris` inherits from `Subject` (observer support is part of the contract), so concrete classes only need `class Tetris(ITetris)`.
  - `tetromino.py`: `ShapeType` enum (I, O, T, S, Z, J, L shapes as 2D tuples) and `Tetromino(ITetromino)` with `rotate()`.
  - `board.py`: `Board(IBoard)` — pure grid engine. Handles collision detection (`is_valid_position`), locking pieces (`place_tetromino`), line clearing (`clear_lines`), and game-over detection. No observer logic.
  - `tetris.py`: `Tetris(ITetris)` — game orchestrator. Owns `Board`, current/next/held `Tetromino`, position, score, level. Fires observer events (string constants defined at top of file) on every state change. Key features: `shadow_row` (ghost piece), `hold()` (hold slot, once per piece), `hard_drop()`, `rotate()` with auto-revert, `play()`/`stop()` for the background tick loop.

- **`OrecchietTetris/utils/`** — shared utilities
  - `observer_subject.py`: `Subject` and `Observer` base classes. `Subject.notify(event_type, data)` calls `observer.update(event_type, data)` on all attached observers.

- **`OrecchietTetris/gui/`** — view layer
  - `TetrisGui(Observer)`: implements `Observer`; reacts to game events from `Tetris`.

### Import hierarchy (no circular dependencies)
```
utils/  ←  interfaces.py  ←  tetromino.py  ←  board.py  ←  tetris.py
```

## Conventions

- All public APIs must be fully type-annotated (mypy strict mode is enforced).
- Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) — `semantic-release` uses them to compute version numbers and publish to PyPI automatically on pushes to `master`.
- Tests live in `tests/` mirroring the package structure (e.g., `tests/model/` for `OrecchietTetris/model/`).
