from __future__ import annotations

from dataclasses import dataclass

Square = tuple[int, int]
Move = tuple[Square, Square]
INITIAL = (
    "rheakaehr", ".........", ".c.....c.", "p.p.p.p.p", ".........",
    ".........", "P.P.P.P.P", ".C.....C.", ".........", "RHEAKAEHR",
)


def side(piece: str) -> str | None:
    return None if piece == "." else "red" if piece.isupper() else "black"


@dataclass(frozen=True)
class Board:
    cells: tuple[str, ...] = tuple("".join(INITIAL))
    current_player: str = "red"

    def __post_init__(self):
        if len(self.cells) != 90 or any(p not in ".KAEHRCPkaehrcp" for p in self.cells):
            raise ValueError("Expected 90 cells using K,A,E,H,R,C,P and lowercase pieces")
        if self.current_player not in ("red", "black"):
            raise ValueError("Player must be red or black")

    @staticmethod
    def other(player: str) -> str:
        return "black" if player == "red" else "red"

    def at(self, square: Square) -> str:
        return self.cells[square[0] * 9 + square[1]]

    def _apply(self, move: Move) -> Board:
        # Đường nội bộ: chỉ gọi với nước đã được bộ sinh nước kiểm tra.
        source, target = move
        cells = list(self.cells)
        cells[target[0] * 9 + target[1]] = self.at(source)
        cells[source[0] * 9 + source[1]] = "."
        return Board(tuple(cells), self.other(self.current_player))

    def legal_moves(self) -> list[Move]:
        from .rules import legal_moves
        return legal_moves(self)

    def play(self, move: Move) -> Board:
        if move not in self.legal_moves():
            raise ValueError(f"Illegal move: {move}")
        return self._apply(move)

    def winner(self) -> str | None:
        if "K" not in self.cells:
            return "black"
        if "k" not in self.cells:
            return "red"
        # Trong cờ tướng, hết nước hợp lệ là thua, kể cả không bị chiếu.
        if not self.legal_moves():
            return self.other(self.current_player)
        return None

    def __str__(self) -> str:
        return "  0 1 2 3 4 5 6 7 8\n" + "\n".join(
            f"{r} " + " ".join(self.cells[r * 9:(r + 1) * 9]) for r in range(10))
