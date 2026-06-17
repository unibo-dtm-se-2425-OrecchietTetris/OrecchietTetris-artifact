"""Tests for OrecchietTetris/__main__.py.

The entry point just imports the package and calls main().  We execute it
via runpy so coverage instruments the __main__ module, and we mock main()
to avoid starting the Kivy event loop.
"""
from __future__ import annotations

import runpy
from unittest.mock import patch

import OrecchietTetris


def test_main_entry_point_calls_main() -> None:
    """Running the package as __main__ must call OrecchietTetris.main()."""
    with patch.object(OrecchietTetris, "main") as mock_main:
        runpy.run_module("OrecchietTetris", run_name="__main__")
    mock_main.assert_called_once()
