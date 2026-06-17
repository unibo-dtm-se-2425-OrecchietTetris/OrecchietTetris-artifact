# Relocate the game timer from the Model to the View

**Date:** 2026-06-15
**Status:** Approved

## Problem

The `Tetris` model owns a self-driving gravity loop running on a background
daemon thread (`play()`, `stop()`, `_game_loop()`, `_stop_event`,
`_game_thread`). This has two issues:

1. **MVC smell.** Real-time timing ("advance the game every N seconds") is a
   control-flow concern, not domain state. A model that runs its own real-time
   loop owns a responsibility that belongs to the controller layer.
2. **Residual thread race.** Gravity ticks mutate model state on the game
   thread while player input mutates the same state on the Kivy UI thread.
   Rendering is already marshalled to the UI thread
   (`game_screen.update` → `Clock.schedule_once`), but state mutation is not.

In Kivy, the `Screen`/`App` widgets legitimately play the controller role and
the framework provides the only real clock (`kivy.clock.Clock`). So the timer
belongs in the view layer, driven by Kivy's Clock on the single UI thread.

## Goals

- Model becomes pure: no threads, no real-time loop. Deterministic and testable
  without sleeping.
- `GameScreen` owns the gravity timer (acting as the game's controller), driving
  `model.tick()` via Kivy `Clock`.
- Single-threaded: the residual state race disappears.
- Behavior preserved: gravity speeds up with level; pause freezes gravity;
  game-over stops the loop.

## Non-goals

- Introducing a separate `controller/` package. (Considered and declined; the
  Screen is the idiomatic Kivy controller.)
- Changing scoring, spawning, line-clear, or rendering logic.

## Design

### Model (`model/tetris.py`)

Remove: `play()`, `stop()`, `_game_loop()`, `_stop_event`, `_game_thread`,
`import threading`.

Keep unchanged: `start()` (reset + spawn first piece), `tick()`,
`tick_interval`, `pause()`, `resume()`, all player actions.

Update `ITetris` interface (`model/interfaces/itetris.py`): drop `play` and
`stop` declarations.

### View (`view/game_screen.py`)

GameScreen owns the timer. Use self-rescheduling `Clock.schedule_once` (not
`schedule_interval`) so each tick is scheduled at the current level's
`tick_interval`, giving automatic speed-up.

```python
def begin(self) -> None:            # replaces model.play()
    self._model.start()
    self._schedule_next_tick()

def end(self) -> None:              # replaces model.stop()
    self._cancel_tick()

def _schedule_next_tick(self) -> None:
    self._tick_event = Clock.schedule_once(self._on_tick, self._model.tick_interval)

def _on_tick(self, dt: float) -> None:
    self._model.tick()
    if not self._model.is_game_over:
        self._schedule_next_tick()

def _cancel_tick(self) -> None:
    if self._tick_event is not None:
        self._tick_event.cancel()
        self._tick_event = None
```

`self._tick_event` initialised to `None` in `__init__`.

- **Pause/resume:** no special handling. `tick()` already no-ops when
  `is_running` is False (paused), so the timer keeps firing harmlessly — same
  behavior as the old thread loop.
- **Game over:** `_on_tick` stops rescheduling; the `GAME_OVER` observer event
  fires as before.

### Lifecycle wiring

Replace every `model.play()` / `model.stop()` call site:

| Call site | Was | Becomes |
|-----------|-----|---------|
| `app._start_game` | `self._model.play()` | `self._game.begin()` |
| `app._back_to_menu` | `self._model.stop()` | `self._game.end()` |
| `game_screen._restart` (try again) | `self._model.play()` | `self.begin()` |
| `game_screen._confirm_quit` | `self._model.stop()` | `self.end()` |

## Testing

- Delete the thread-loop tests (`tests/model/test_tetris.py`, the `play`/`stop`/
  `_game_thread` block). Existing `tick` / `tick_interval` model tests stay.
- Add GameScreen tests covering `begin` (starts game + schedules a tick),
  `_on_tick` (advances model, reschedules while running, stops at game over),
  and `end` (cancels the pending tick). Drive Kivy's Clock deterministically
  (`Clock.tick` or a mocked event) rather than sleeping.
- Maintain existing coverage level (project is at 100%).

## Risk / rollback

Small, self-contained change (~40 lines removed from model, ~15 added to view,
interface + tests updated). Rollback = revert the commit. No data or schema
impact.
