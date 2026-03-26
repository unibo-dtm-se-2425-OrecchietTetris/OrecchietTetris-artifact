# Design: Replace custom I18n with python-i18n direct API

**Date:** 2026-03-26

## Overview

Replace the custom `I18n` wrapper class in `view/i18n.py` with direct use of the `python-i18n` library API. The library is already declared as a dependency in `pyproject.toml` but unused.

## Files added

- `OrecchietTetris/view/locales/en.yml` — English translations
- `OrecchietTetris/view/locales/it.yml` — Italian translations

Both files use the same keys as the current `_STRINGS` dict (`new_game`, `language`, `pause`, `resume`, `game_over`, `score`, `level`, `lines`, `hold`, `next`, `back_to_menu`).

`python-i18n` is configured with `filename_format = '{locale}.{format}'` (no namespace), so keys are accessed as `i18n.t('new_game')` when locale is `en`.

## Files deleted

- `OrecchietTetris/view/i18n.py` — custom wrapper, no longer needed
- `tests/view/test_i18n.py` — tests would only exercise the third-party library, not our code

## Files modified

### `OrecchietTetris/view/app.py`

Configure `python-i18n` once at the start of `TetrisApp.build()` before constructing any screens:

```python
i18n.set('file_format', 'yml')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('load_path', [str(Path(__file__).parent / 'locales')])
i18n.set('locale', 'en')
i18n.set('fallback', 'en')
```

Remove `I18n` import, instantiation, and `i18n=` argument from both screen constructors.

### `OrecchietTetris/view/menu_screen.py`

- Remove `I18n` import and `i18n: I18n` constructor parameter
- Replace all `self._i18n.t("key")` → `i18n.t("key")`
- Replace `self._i18n.set_language(lang)` → `i18n.set('locale', lang)`
- Replace `self._i18n.language == "en"` → `i18n.get('locale') == 'en'`

### `OrecchietTetris/view/game_screen.py`

- Remove `I18n` import and `i18n: I18n` constructor parameter
- Replace all `self._i18n.t("key")` → `i18n.t("key")`

### `OrecchietTetris/view/__init__.py`

Remove `I18n` from imports and `__all__`.

## README

No changes needed. The README describes the EN/IT language-switching feature, not the internal implementation.

## Out of scope

- Adding new languages
- Adding new translation keys
- YAML data-validation tests (low value, can be added later if needed)
