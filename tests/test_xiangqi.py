import unittest
from xiangqi_ai.board import Board
from xiangqi_ai.rules import pseudo_moves, in_check
from xiangqi_ai.minimax import MinimaxAgent
from xiangqi_ai.mcts import MCTS
from xiangqi_ai.heuristics import evaluate


def position(pieces, player="red"):
    cells = ["."] * 90
    for (r, c), piece in pieces.items():
        cells[r * 9 + c] = piece
    return Board(tuple(cells), player)


class XiangqiTests(unittest.TestCase):
    def test_initial_position(self):
        board = Board()
        self.assertEqual(sum(p != "." for p in board.cells), 32)
        self.assertEqual(len(board.legal_moves()), 44)
        self.assertFalse(in_check(board, "red"))
        self.assertEqual(evaluate(board, "red"), 0)

    def test_horse_leg(self):
        board = position({(7, 4): "H", (6, 4): "P"})
        moves = pseudo_moves(board, "red")
        self.assertNotIn(((7, 4), (5, 3)), moves)
        self.assertIn(((7, 4), (8, 6)), moves)

    def test_initial_second_ply_move_count(self):
        board = Board()
        self.assertEqual(sum(len(board._apply(m).legal_moves()) for m in board.legal_moves()), 1920)

    def test_black_rules_mirror_red_rules(self):
        board = Board()
        mirrored = Board(tuple(p.swapcase() for p in reversed(board.cells)), "black")
        expected = {((9-a[0], 8-a[1]), (9-b[0], 8-b[1])) for a, b in board.legal_moves()}
        self.assertEqual(set(mirrored.legal_moves()), expected)

    def test_elephant_eye_and_river(self):
        board = position({(5, 4): "E", (6, 5): "P"})
        moves = pseudo_moves(board, "red")
        self.assertNotIn(((5, 4), (7, 6)), moves)
        self.assertNotIn(((5, 4), (3, 2)), moves)
        self.assertIn(((5, 4), (7, 2)), moves)

    def test_cannon_screen(self):
        for screens, allowed in (([], False), ([(5, 2)], True), ([(5, 2), (5, 3)], False)):
            board = position({(5, 0): "C", (5, 5): "r", **{s: "P" for s in screens}})
            self.assertEqual(((5, 0), (5, 5)) in pseudo_moves(board, "red"), allowed)

    def test_pawn_river(self):
        board = position({(6, 0): "P", (4, 4): "P", (5, 8): "p"})
        moves = pseudo_moves(board, "red")
        self.assertNotIn(((6, 0), (6, 1)), moves)
        self.assertIn(((4, 4), (4, 5)), moves)
        self.assertNotIn(((4, 4), (5, 4)), moves)
        self.assertIn(((5, 8), (5, 7)), pseudo_moves(board, "black"))

    def test_palace(self):
        board = position({(9, 3): "K", (8, 3): "A"})
        moves = pseudo_moves(board, "red")
        self.assertNotIn(((9, 3), (9, 2)), moves)
        self.assertIn(((8, 3), (7, 4)), moves)
        self.assertNotIn(((8, 3), (7, 2)), moves)

    def test_facing_generals(self):
        board = position({(9, 4): "K", (0, 4): "k", (5, 4): "R"})
        self.assertNotIn(((5, 4), (5, 3)), board.legal_moves())
        with self.assertRaises(ValueError):
            board.play(((5, 4), (5, 3)))

    def test_check_requires_response(self):
        board = position({(9, 4): "K", (0, 3): "k", (5, 4): "r", (8, 0): "R"})
        self.assertTrue(in_check(board, "red"))
        self.assertNotIn(((8, 0), (7, 0)), board.legal_moves())

    def test_stalemate_is_loss(self):
        board = position({(0, 4): "k", (9, 3): "K", (2, 3): "R", (2, 5): "R", (1, 0): "R"}, "black")
        self.assertFalse(in_check(board, "black"))
        self.assertEqual(board.legal_moves(), [])
        self.assertEqual(board.winner(), "red")

    def test_agents_return_legal_moves(self):
        board = Board()
        agent = MCTS(iterations=5, rollout_steps=2)
        self.assertIn(agent.choose_move(board), board.legal_moves())
        self.assertEqual(sum(c.visits for c in agent.root.children), 5)
        self.assertIn(MinimaxAgent(depth=1).choose_move(board), board.legal_moves())

    def test_minimax_finishes_win(self):
        board = position({(0, 4): "k", (9, 3): "K", (2, 4): "R"})
        move = MinimaxAgent(depth=1).choose_move(board)
        self.assertEqual(board.play(move).winner(), "red")

    def test_uct_revisits_children_after_expansion(self):
        board = Board()
        agent = MCTS(iterations=50, rollout="random", rollout_steps=1)
        self.assertIn(agent.choose_move(board), board.legal_moves())
        self.assertEqual(len(agent.root.children), 44)
        self.assertEqual(sum(child.visits for child in agent.root.children), 50)
        self.assertTrue(any(child.visits > 1 for child in agent.root.children))


if __name__ == "__main__":
    unittest.main()
