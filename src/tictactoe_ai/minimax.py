from __future__ import annotations

from dataclasses import dataclass
from math import inf

from .board import Board, Move
from .heuristics import WIN_SCORE, evaluate, immediate_winning_move


@dataclass(slots=True)
class MinimaxConfig:
    max_depth: int | None = None
    alpha_beta: bool = True
    candidate_radius: int = 1


@dataclass(slots=True)
class SearchStats:
    nodes: int = 0
    cutoffs: int = 0


class MinimaxAgent:
    def __init__(self, config: MinimaxConfig | None = None) -> None:
        self.config = config or MinimaxConfig()
        self.stats = SearchStats()

    def choose_move(self, board: Board) -> Move:
        if board.is_terminal():
            raise ValueError("cannot choose a move from a terminal board")
        self.stats = SearchStats()
        root_player = board.current_player
        depth = self.config.max_depth
        if depth is None:
            # Giải chính xác bàn 3x3; bàn lớn dùng tìm kiếm giới hạn độ sâu.
            depth = len(board.legal_moves()) if board.size == 3 else 3

        moves = self._ordered_moves(board)
        forced = immediate_winning_move(board, moves)
        if forced is not None:
            return forced

        best_move = moves[0]
        best_score = -inf
        alpha, beta = -inf, inf
        # Nút gốc chọn nước có giá trị Minimax lớn nhất.
        for move in moves:
            score = self._search(board.play(move), depth - 1, alpha, beta, root_player)
            if score > best_score:
                best_score, best_move = score, move
            if self.config.alpha_beta:
                alpha = max(alpha, best_score)
        return best_move

    def _search(self, board: Board, depth: int, alpha: float, beta: float, root_player: str) -> float:
        self.stats.nodes += 1
        # Dừng ở trạng thái kết thúc hoặc khi đạt giới hạn độ sâu.
        winner = board.winner()
        if winner == root_player:
            return WIN_SCORE + depth
        if winner == Board.other(root_player):
            return -WIN_SCORE - depth
        if board.is_full():
            return 0
        if depth <= 0:
            return evaluate(board, root_player)

        maximizing = board.current_player == root_player
        value = -inf if maximizing else inf
        for move in self._ordered_moves(board):
            child = self._search(board.play(move), depth - 1, alpha, beta, root_player)
            if maximizing:
                value = max(value, child)
                alpha = max(alpha, value)
            else:
                value = min(value, child)
                beta = min(beta, value)
            if self.config.alpha_beta and beta <= alpha:
                # Nhánh còn lại không thể thay đổi quyết định hiện tại.
                self.stats.cutoffs += 1
                break
        return value

    def _ordered_moves(self, board: Board) -> list[Move]:
        moves = board.candidate_moves(self.config.candidate_radius)
        player = board.current_player
        center = (board.size - 1) / 2
        # Xét nước thắng và nước có heuristic tốt trước để Alpha-Beta cắt nhiều hơn.
        return sorted(
            moves,
            key=lambda move: (
                board.play(move).winner() == player,
                evaluate(board.play(move), player),
                -(abs(move[0] - center) + abs(move[1] - center)),
            ),
            reverse=True,
        )

