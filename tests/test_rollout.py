import random
import unittest
from tictactoe_ai.board import Board
from tictactoe_ai.heuristics import heuristic_rollout_move
from tictactoe_ai.experiments import compare_rollouts, run_match_series


class RolloutTests(unittest.TestCase):
    def test_win_before_block(self):
        board = Board.from_rows(["XX.", "OO.", "..."], win_length=3)
        self.assertEqual(heuristic_rollout_move(board, random.Random(1)), (0, 2))

    def test_blocks_five_in_a_row(self):
        board = Board.from_rows(["OOOO.", ".....", "..X..", ".....", "....."], win_length=5)
        self.assertEqual(heuristic_rollout_move(board, random.Random(1)), (0, 4))

    def test_delta_can_be_negative(self):
        common = dict(size=3, win_length=3, c=1.4, iterations=100, games=50, avg_seconds=1.0)
        rows = [dict(common, rollout="random", win_rate=0.8, non_loss_rate=1.0),
                dict(common, rollout="heuristic", win_rate=0.7, non_loss_rate=0.9)]
        result = compare_rollouts(rows)[0]
        self.assertAlmostEqual(result["win_rate_delta_pp"], -10)

    def test_series_records_all_games(self):
        row = run_match_series(2, 3, 1.4, "heuristic", 1, 5, 5)
        self.assertEqual(row["wins"] + row["draws"] + row["losses"], 2)
        self.assertEqual(row["size"], 5)
