from __future__ import annotations

import random
from collections.abc import Sequence

from .board import Board, EMPTY, Move

WIN_SCORE = 1_000_000


def evaluate(board: Board, player: str) -> int:
    # Trạng thái thắng/thua phải lấn át mọi điểm heuristic khác.
    winner = board.winner()
    if winner == player:
        return WIN_SCORE
    if winner == Board.other(player):
        return -WIN_SCORE

    score = 0
    opponent = Board.other(player)
    k = board.win_length
    weights = [0] + [10**i for i in range(k)]
    # Thưởng các cửa sổ chỉ chứa quân ta, trừ điểm các cửa sổ chỉ chứa đối thủ.
    for window in iter_windows(board):
        own = window.count(player)
        rival = window.count(opponent)
        if own and rival:
            continue
        if own:
            score += weights[own]
        elif rival:
            score -= weights[rival]
    return score


def iter_windows(board: Board):
    n, k = board.size, board.win_length
    directions = ((1, 0), (0, 1), (1, 1), (1, -1))
    for row in range(n):
        for col in range(n):
            for dr, dc in directions:
                end_r = row + (k - 1) * dr
                end_c = col + (k - 1) * dc
                if 0 <= end_r < n and 0 <= end_c < n:
                    yield [board.at((row + i * dr, col + i * dc)) for i in range(k)]


def immediate_winning_move(board: Board, moves: Sequence[Move] | None = None) -> Move | None:
    for move in moves or board.candidate_moves():
        if board.play(move).winner() == board.current_player:
            return move
    return None


def heuristic_rollout_move(board: Board, rng: random.Random) -> Move:
    moves = board.candidate_moves()
    # Ưu tiên thắng ngay, sau đó chặn nước thắng ngay của đối thủ.
    winning = immediate_winning_move(board, moves)
    if winning is not None:
        return winning

    opponent = Board.other(board.current_player)
    blocking: list[Move] = []
    for move in moves:
        idx = move[0] * board.size + move[1]
        cells = list(board.cells)
        cells[idx] = opponent
        probe = Board(board.size, board.win_length, tuple(cells), board.current_player, move)
        if probe.winner() == opponent:
            blocking.append(move)
    if blocking:
        return rng.choice(blocking)

    # Chọn nước tạo nhiều chuỗi có lợi; trung tâm chỉ dùng khi bằng điểm.
    center = (board.size - 1) / 2
    def score(move: Move) -> tuple[int, float]:
        return (evaluate(board.play(move), board.current_player),
                -abs(move[0] - center) - abs(move[1] - center))
    scores = {move: score(move) for move in moves}
    highest = max(scores.values())
    best = [move for move in moves if scores[move] == highest]
    return rng.choice(best)

