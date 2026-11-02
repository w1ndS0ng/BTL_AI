import unittest

from tictactoe_ai.board import Board
from tictactoe_ai.minimax import MinimaxAgent, MinimaxConfig


class MinimaxTests(unittest.TestCase):
    def test_minimax_takes_immediate_win(self):
        board = Board.from_rows(["XX.", "OO.", "..."], current_player="X", win_length=3)
        self.assertEqual(MinimaxAgent().choose_move(board), (0, 2))

    def test_minimax_blocks_loss(self):
        board = Board.from_rows(["OO.", "X..", ".X."], current_player="X", win_length=3)
        self.assertEqual(MinimaxAgent().choose_move(board), (0, 2))

    def test_alpha_beta_visits_no_more_nodes(self):
        plain = MinimaxAgent(MinimaxConfig(alpha_beta=False))
        pruned = MinimaxAgent(MinimaxConfig(alpha_beta=True))
        board = Board(3, 3)
        plain.choose_move(board)
        pruned.choose_move(board)
        self.assertLessEqual(pruned.stats.nodes, plain.stats.nodes)
        self.assertGreater(pruned.stats.cutoffs, 0)


if __name__ == "__main__":
    unittest.main()

