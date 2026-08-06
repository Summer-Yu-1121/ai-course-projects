import sys
import os

# Allow tests to import modules from the starter directory
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "starter"))

import sudoku_logic


def test_create_empty_board_returns_9x9_grid():
    board = sudoku_logic.create_empty_board()
    assert len(board) == 9
    assert all(len(row) == 9 for row in board)