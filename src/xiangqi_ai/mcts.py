import math
import random
from dataclasses import dataclass, field
from .board import Board, Move
from .heuristics import evaluate, rollout_move


@dataclass
class Node:
    board: Board
    parent: "Node | None" = None
    move: Move | None = None
    visits: int = 0
    wins: float = 0.0
    children: list = field(default_factory=list)
    untried: list = field(init=False)

    def __post_init__(self):
        self.untried = self.board.legal_moves()


class MCTS:
    def __init__(self, iterations=100, c=1.4, rollout="heuristic", seed=42, rollout_steps=30):
        if iterations < 1 or rollout_steps < 1 or c < 0 or rollout not in ("random", "heuristic"):
            raise ValueError("Invalid MCTS configuration")
        self.iterations, self.c, self.rollout_steps = iterations, c, rollout_steps
        self.rollout = rollout
        self.rng = random.Random(seed)
        self.root = None

    def choose_move(self, board: Board) -> Move:
        if board.winner() is not None:
            raise ValueError("Terminal position")
        self.root = root = Node(board)
        for _ in range(self.iterations):
            node = root
            # Selection và expansion: W của con thuộc bên vừa đi vào nút con.
            while not node.untried and node.children:
                node = max(node.children, key=lambda n: n.wins / n.visits
                           + self.c * math.sqrt(math.log(node.visits) / n.visits))
            if node.untried:
                move = node.untried.pop(self.rng.randrange(len(node.untried)))
                child = Node(node.board._apply(move), node, move)
                node.children.append(child)
                node = child
            state = node.board
            winner = state.winner()
            # Rollout có giới hạn để tránh ván mô phỏng kéo dài vô hạn.
            for _ in range(self.rollout_steps):
                if winner:
                    break
                moves = state.legal_moves()
                move = rollout_move(state, moves, self.rng) if self.rollout == "heuristic" else self.rng.choice(moves)
                state = state._apply(move)
                winner = state.winner()
            # Khi hết ngân sách, dùng lượng giá mềm thay vì giả định hòa.
            while node is not None:
                player = Board.other(node.board.current_player)
                reward = (float(winner == player) if winner else
                          0.5 + 0.5 * math.tanh(evaluate(state, player) / 1500))
                node.visits += 1
                node.wins += reward
                node = node.parent
        return max(root.children, key=lambda n: n.visits).move
