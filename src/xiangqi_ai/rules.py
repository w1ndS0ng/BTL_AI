"""Sinh nước theo luật quân cờ, sau đó loại nước để tướng mình bị chiếu."""
from .board import Board, Move, Square, side


def inside(r: int, c: int) -> bool:
    return 0 <= r < 10 and 0 <= c < 9


def palace(r: int, c: int, player: str) -> bool:
    return 3 <= c <= 5 and (7 <= r <= 9 if player == "red" else 0 <= r <= 2)


def pseudo_moves(board: Board, player: str) -> list[Move]:
    moves = []
    for index, piece in enumerate(board.cells):
        if side(piece) != player:
            continue
        r, c = divmod(index, 9)
        kind = piece.upper()
        targets: list[Square] = []
        if kind in ("R", "C"):
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc, screen = r + dr, c + dc, False
                while inside(nr, nc):
                    occupant = board.at((nr, nc))
                    if kind == "R":
                        targets.append((nr, nc))
                        if occupant != ".":
                            break
                    elif not screen:
                        if occupant == ".":
                            targets.append((nr, nc))
                        else:
                            screen = True
                    elif occupant != ".":
                        # Pháo bắt quân phải nhảy đúng một ngòi.
                        targets.append((nr, nc))
                        break
                    nr, nc = nr + dr, nc + dc
        elif kind == "H":
            for dr, dc in ((2, 1), (2, -1), (-2, 1), (-2, -1),
                           (1, 2), (-1, 2), (1, -2), (-1, -2)):
                leg = (r + (dr // 2 if abs(dr) == 2 else 0),
                       c + (dc // 2 if abs(dc) == 2 else 0))
                if inside(r + dr, c + dc) and board.at(leg) == ".":
                    targets.append((r + dr, c + dc))
        elif kind == "E":
            for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
                nr, nc = r + dr, c + dc
                if (inside(nr, nc) and (nr >= 5 if player == "red" else nr <= 4)
                        and board.at((r + dr // 2, c + dc // 2)) == "."):
                    targets.append((nr, nc))
        elif kind in ("K", "A"):
            directions = ((1, 0), (-1, 0), (0, 1), (0, -1)) if kind == "K" else ((1, 1), (1, -1), (-1, 1), (-1, -1))
            targets.extend((r + dr, c + dc) for dr, dc in directions
                           if palace(r + dr, c + dc, player))
            if kind == "K":
                # Hai tướng cùng cột không có quân chắn sẽ chiếu nhau.
                for dr in (-1, 1):
                    nr = r + dr
                    while inside(nr, c):
                        occupant = board.at((nr, c))
                        if occupant != ".":
                            if occupant.upper() == "K" and side(occupant) != player:
                                targets.append((nr, c))
                            break
                        nr += dr
        else:  # Tốt chỉ đi ngang sau khi qua sông, không được lùi.
            dr = -1 if player == "red" else 1
            targets.append((r + dr, c))
            crossed_river = r <= 4 if player == "red" else r >= 5
            if crossed_river:
                targets.extend(((r, c - 1), (r, c + 1)))
        moves.extend(((r, c), target) for target in targets
                     if inside(*target) and side(board.at(target)) != player)
    return moves


def in_check(board: Board, player: str) -> bool:
    king = "K" if player == "red" else "k"
    if king not in board.cells:
        return True
    square = divmod(board.cells.index(king), 9)
    return any(target == square for _, target in pseudo_moves(board, Board.other(player)))


def legal_moves(board: Board) -> list[Move]:
    if "K" not in board.cells or "k" not in board.cells:
        return []
    return [move for move in pseudo_moves(board, board.current_player)
            if not in_check(board._apply(move), board.current_player)]
