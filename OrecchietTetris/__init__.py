import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('OrecchietTetris')


def main() -> None:
    """Launch the Kivy GUI application."""
    from OrecchietTetris.view.app import TetrisApp
    TetrisApp().run()


# let this be the last line of this file
logger.info("OrecchietTetris loaded")
