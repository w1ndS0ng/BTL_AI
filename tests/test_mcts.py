import unittest

from tictactoe_ai.board import Board
from tictactoe_ai.mcts import MCTS, MCTSConfig


class MCTSTests(unittest.TestCase):
    def test_mcts_takes_immediate_win(self):
        board = Board.from_rows(["XX.", "OO.", "..."], current_player="X", win_length=3)
        agent = MCTS(MCTSConfig(iterations=20, seed=1))
        self.assertEqual(agent.choose_move(board), (0, 2))

    def test_mcts_blocks_immediate_loss(self):
        board = Board.from_rows(["OO.", "X..", ".X."], current_player="X", win_length=3)
        agent = MCTS(MCTSConfig(iterations=20, seed=1))
        self.assertEqual(agent.choose_move(board), (0, 2))

    def test_root_statistics_have_visits(self):
        agent = MCTS(MCTSConfig(iterations=50, seed=2))
        move = agent.choose_move(Board(3, 3))
        self.assertIn(move, Board(3, 3).legal_moves())
        self.assertEqual(sum(row["N"] for row in agent.root_statistics()), 50)


if __name__ == "__main__":
    unittest.main()

