from __future__ import annotations


_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "new_game": "New Game",
        "language": "Language",
        "pause": "Pause",
        "resume": "Resume",
        "game_over": "Game Over",
        "score": "Score",
        "level": "Level",
        "lines": "Lines",
        "hold": "Hold",
        "next": "Next",
        "back_to_menu": "Back to Menu",
    },
    "it": {
        "new_game": "Nuova Partita",
        "language": "Lingua",
        "pause": "Pausa",
        "resume": "Riprendi",
        "game_over": "Partita Finita",
        "score": "Punteggio",
        "level": "Livello",
        "lines": "Righe",
        "hold": "Tieni",
        "next": "Prossimo",
        "back_to_menu": "Menu Principale",
    },
}

_SUPPORTED_LANGUAGES = ("en", "it")


class I18n:
    """Simple runtime-switchable localization helper.

    Usage::

        i18n = I18n()
        i18n.set_language("it")
        print(i18n.t("new_game"))  # "Nuova Partita"
    """

    def __init__(self, language: str = "en") -> None:
        if language not in _SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{language}'. Choose from {_SUPPORTED_LANGUAGES}")
        self._language = language

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, lang: str) -> None:
        """Switch the active language.  Raises ``ValueError`` for unknown codes."""
        if lang not in _SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{lang}'. Choose from {_SUPPORTED_LANGUAGES}")
        self._language = lang

    def t(self, key: str) -> str:
        """Return the translated string for *key* in the active language.

        Falls back to the key itself if the translation is missing.
        """
        return _STRINGS.get(self._language, {}).get(key, key)
