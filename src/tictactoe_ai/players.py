from __future__ import annotations

import random

from .board import Board, Move


class RandomPlayer:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def choose_move(self, board: Board) -> Move:
        return self.rng.choice(board.candidate_moves())


class HumanPlayer:
    def choose_move(self, board: Board) -> Move:
        while True:
            raw = input(f"{board.current_player}, enter row and column: ").strip().replace(",", " ")
            try:
                row, col = (int(value) for value in raw.split())
                move = (row, col)
                if move in board.legal_moves():
                    return move
            except (ValueError, TypeError):
                pass
            print("Invalid move. Example: 4 4")

