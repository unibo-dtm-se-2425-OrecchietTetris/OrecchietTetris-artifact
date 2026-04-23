from OrecchietTetris.view.widgets.board_widget import BOARD_ROWS, BOARD_COLS, BOARD_PADDING


def test_board_constants():
    assert BOARD_ROWS == 20
    assert BOARD_COLS == 10
    assert BOARD_PADDING == 12
