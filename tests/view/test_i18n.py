import pytest
from OrecchietTetris.view.i18n import I18n


def test_default_language_is_english():
    i18n = I18n()
    assert i18n.language == "en"


def test_translate_english_keys():
    i18n = I18n("en")
    assert i18n.t("new_game") == "New Game"
    assert i18n.t("pause") == "Pause"
    assert i18n.t("resume") == "Resume"
    assert i18n.t("game_over") == "Game Over"
    assert i18n.t("score") == "Score"
    assert i18n.t("level") == "Level"
    assert i18n.t("lines") == "Lines"
    assert i18n.t("hold") == "Hold"
    assert i18n.t("next") == "Next"
    assert i18n.t("language") == "Language"


def test_translate_italian_keys():
    i18n = I18n("it")
    assert i18n.t("new_game") == "Nuova Partita"
    assert i18n.t("pause") == "Pausa"
    assert i18n.t("resume") == "Riprendi"
    assert i18n.t("game_over") == "Partita Finita"
    assert i18n.t("score") == "Punteggio"
    assert i18n.t("level") == "Livello"
    assert i18n.t("lines") == "Righe"
    assert i18n.t("hold") == "Tieni"
    assert i18n.t("next") == "Prossimo"
    assert i18n.t("language") == "Lingua"


def test_switch_language_at_runtime():
    i18n = I18n("en")
    assert i18n.t("new_game") == "New Game"
    i18n.set_language("it")
    assert i18n.language == "it"
    assert i18n.t("new_game") == "Nuova Partita"
    i18n.set_language("en")
    assert i18n.t("new_game") == "New Game"


def test_unknown_key_falls_back_to_key():
    i18n = I18n("en")
    assert i18n.t("nonexistent_key") == "nonexistent_key"


def test_unsupported_language_raises():
    with pytest.raises(ValueError):
        I18n("de")


def test_set_unsupported_language_raises():
    i18n = I18n("en")
    with pytest.raises(ValueError):
        i18n.set_language("fr")
