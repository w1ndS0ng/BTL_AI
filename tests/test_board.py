import unittest

from tictactoe_ai.board import Board


class BoardTests(unittest.TestCase):
    def test_detects_wins(self):
        cases = [
            ["...", "...", "XXX"],
            [".X.", ".X.", ".X."],
            ["X..", ".X.", "..X"],
            ["..X", ".X.", "X.."],
        ]
        for rows in cases:
            with self.subTest(rows=rows):
                board = Board.from_rows(rows, current_player="O", win_length=3)
                self.assertEqual(board.winner(), "X")

    def test_five_in_a_row_on_large_board(self):
        board = Board(9, 5)
        for col in range(5):
            board = board.play((4, col))
            if col < 4:
                board = board.play((0, col))
        self.assertEqual(board.winner(), "X")


if __name__ == "__main__":
    unittest.main()

