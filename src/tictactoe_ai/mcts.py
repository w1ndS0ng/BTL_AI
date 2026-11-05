from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from .board import Board, Move
from .heuristics import heuristic_rollout_move, immediate_winning_move


@dataclass(slots=True)
class MCTSConfig:
    iterations: int = 1000
    exploration_c: float = math.sqrt(2)
    rollout: str = "random"
    seed: int | None = None
    max_rollout_steps: int | None = None


@dataclass(slots=True)
class Node:
    state: Board
    parent: Node | None = None
    move: Move | None = None
    player_just_moved: str = "O"
    wins: float = 0.0
    visits: int = 0
    children: list[Node] = field(default_factory=list)
    untried_moves: list[Move] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.untried_moves and not self.state.is_terminal():
            self.untried_moves = self.state.candidate_moves()

    def uct_child(self, c: float) -> Node:
        log_parent = math.log(max(1, self.visits))
        # UCT cân bằng khai thác W/N và khám phá các nút ít được thăm.
        return max(
            self.children,
            key=lambda child: (child.wins / child.visits) + c * math.sqrt(log_parent / child.visits),
        )


class MCTS:
    def __init__(self, config: MCTSConfig | None = None) -> None:
        self.config = config or MCTSConfig()
        if self.config.rollout not in {"random", "heuristic"}:
            raise ValueError("rollout must be random or heuristic")
        self.rng = random.Random(self.config.seed)
        self.root: Node | None = None

    def choose_move(self, board: Board) -> Move:
        self.root = None
        if board.is_terminal():
            raise ValueError("cannot choose a move from a terminal board")
        moves = board.candidate_moves()
        winning = immediate_winning_move(board, moves)
        if winning is not None:
            return winning
        blocking = self._immediate_block(board, moves)
        if blocking is not None:
            return blocking

        root = Node(board, player_just_moved=Board.other(board.current_player))
        self.root = root
        for _ in range(self.config.iterations):
            node = root
            state = board

            # 1. Selection: đi xuống cây bằng công thức UCT.
            while not node.untried_moves and node.children:
                node = node.uct_child(self.config.exploration_c)
                state = node.state

            # 2. Expansion: thêm một nước chưa được thử vào cây.
            if node.untried_moves and not state.is_terminal():
                index = self.rng.randrange(len(node.untried_moves))
                move = node.untried_moves.pop(index)
                state = state.play(move)
                child = Node(state, node, move, Board.other(state.current_player))
                node.children.append(child)
                node = child

            # 3. Simulation: chơi tiếp đến khi ván kết thúc.
            terminal = self._rollout(state)
            # 4. Backpropagation: cập nhật W và N từ lá về gốc.
            while node is not None:
                node.visits += 1
                node.wins += terminal.result_for(node.player_just_moved)
                node = node.parent

        if not root.children:
            return self.rng.choice(moves)
        # Chọn N lớn nhất vì đây là nước được cây tìm kiếm tin cậy nhất.
        return max(root.children, key=lambda child: child.visits).move  # type: ignore[return-value]

    def root_statistics(self) -> list[dict[str, float | int | Move]]:
        if self.root is None:
            return []
        rows = []
        for child in sorted(self.root.children, key=lambda item: item.visits, reverse=True):
            rows.append(
                {
                    "move": child.move,
                    "W": child.wins,
                    "N": child.visits,
                    "W/N": child.wins / child.visits if child.visits else 0.0,
                }
            )
        return rows

    def _rollout(self, state: Board) -> Board:
        steps = 0
        limit = self.config.max_rollout_steps or state.size * state.size
        while not state.is_terminal() and steps < limit:
            moves = state.candidate_moves()
            # Cho phép so sánh rollout ngẫu nhiên và rollout có tri thức đơn giản.
            if self.config.rollout == "heuristic":
                move = heuristic_rollout_move(state, self.rng)
            else:
                move = self.rng.choice(moves)
            state = state.play(move)
            steps += 1
        return state

    @staticmethod
    def _immediate_block(board: Board, moves: list[Move]) -> Move | None:
        opponent = Board.other(board.current_player)
        for move in moves:
            idx = move[0] * board.size + move[1]
            cells = list(board.cells)
            cells[idx] = opponent
            probe = Board(board.size, board.win_length, tuple(cells), board.current_player, move)
            if probe.winner() == opponent:
                return move
        return None

