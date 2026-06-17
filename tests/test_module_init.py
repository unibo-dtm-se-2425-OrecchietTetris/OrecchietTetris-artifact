"""Tests for OrecchietTetris/__init__.py.

The module sets up logging and exposes main(), which launches the Kivy app.
We verify that main() delegates to TetrisApp().run() without actually
starting the Kivy event loop.
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch


def test_logger_is_configured() -> None:
    import OrecchietTetris
    assert OrecchietTetris.logger is not None
    assert OrecchietTetris.logger.name == "OrecchietTetris"


def test_main_creates_and_runs_tetrisapp() -> None:
    """main() must instantiate TetrisApp and call .run() on it."""
    mock_tetrisapp_cls = MagicMock()
    mock_app_module = MagicMock()
    mock_app_module.TetrisApp = mock_tetrisapp_cls

    with patch.dict(sys.modules, {"OrecchietTetris.view.app": mock_app_module}):
        import OrecchietTetris
        OrecchietTetris.main()

    mock_tetrisapp_cls.assert_called_once()
    mock_tetrisapp_cls.return_value.run.assert_called_once()
