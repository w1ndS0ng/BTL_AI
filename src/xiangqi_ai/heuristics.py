import random
from .board import Board, Move, side

VALUES = {"K": 100000, "R": 900, "C": 450, "H": 400, "A": 200, "E": 200, "P": 100}


def evaluate(board: Board, player: str) -> int:
    """Điểm quân + thưởng tốt qua sông và tiến quân, tính theo góc nhìn player."""
    total = 0
    for i, piece in enumerate(board.cells):
        if piece == ".":
            continue
        r, c = divmod(i, 9)
        owner = side(piece)
        advance = 9 - r if owner == "red" else r
        value = VALUES[piece.upper()]
        if piece.upper() == "P":
            value += 15 * advance + (100 if advance >= 5 else 0)
        if piece.upper() in ("R", "H", "C"):
            value += 4 * (4 - abs(c - 4))
        total += value if owner == player else -value
    return total


def rollout_move(board: Board, moves: list[Move], rng: random.Random) -> Move:
    # Bắt quân giá trị cao trước; phá hòa ngẫu nhiên để rollout đa dạng.
    scores = {move: VALUES.get(board.at(move[1]).upper(), 0) * 10
              + evaluate(board._apply(move), board.current_player) for move in moves}
    best = max(scores.values())
    return rng.choice([move for move in moves if scores[move] == best])
