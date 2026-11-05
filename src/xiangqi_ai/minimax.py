from math import inf
from .board import Board, Move
from .heuristics import evaluate


class MinimaxAgent:
    def __init__(self, depth: int = 2):
        if depth < 1:
            raise ValueError("depth must be positive")
        self.depth = depth
        self.nodes = self.cutoffs = 0

    def choose_move(self, board: Board) -> Move:
        if board.winner() is not None:
            raise ValueError("Terminal position")
        self.nodes = self.cutoffs = 0
        player = board.current_player

        def search(state, depth, alpha, beta):
            self.nodes += 1
            winner = state.winner()
            if winner:
                return (1000000 + depth) * (1 if winner == player else -1)
            if depth == 0:
                return evaluate(state, player)
            maximizing = state.current_player == player
            value = -inf if maximizing else inf
            moves = sorted(state.legal_moves(),
                           key=lambda m: evaluate(state._apply(m), state.current_player), reverse=True)
            for move in moves:
                score = search(state._apply(move), depth - 1, alpha, beta)
                value = max(value, score) if maximizing else min(value, score)
                if maximizing:
                    alpha = max(alpha, value)
                else:
                    beta = min(beta, value)
                if alpha >= beta:
                    self.cutoffs += 1
                    break
            return value

        best, best_score, alpha = None, -inf, -inf
        for move in sorted(board.legal_moves(), key=lambda m: evaluate(board._apply(m), player), reverse=True):
            score = search(board._apply(move), self.depth - 1, alpha, inf)
            if score > best_score:
                best, best_score = move, score
            alpha = max(alpha, score)
        return best
