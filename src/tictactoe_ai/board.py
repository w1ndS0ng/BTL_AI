from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

Move = tuple[int, int]
EMPTY = "."
PLAYERS = ("X", "O")


@dataclass(frozen=True, slots=True)
class Board:
    size: int = 9
    win_length: int = 5
    cells: tuple[str, ...] | None = None
    current_player: str = "X"
    last_move: Move | None = None

    def __post_init__(self) -> None:
        if self.size < 3:
            raise ValueError("size must be at least 3")
        if not 2 <= self.win_length <= self.size:
            raise ValueError("win_length must be between 2 and size")
        if self.current_player not in PLAYERS:
            raise ValueError("current_player must be X or O")
        if self.cells is None:
            object.__setattr__(self, "cells", (EMPTY,) * (self.size * self.size))
        elif len(self.cells) != self.size * self.size:
            raise ValueError("cells length does not match board size")

    @staticmethod
    def other(player: str) -> str:
        return "O" if player == "X" else "X"

    def at(self, move: Move) -> str:
        row, col = move
        return self.cells[row * self.size + col]  # type: ignore[index]

    def legal_moves(self) -> list[Move]:
        return [divmod(i, self.size) for i, value in enumerate(self.cells) if value == EMPTY]  # type: ignore[arg-type]

    def candidate_moves(self, radius: int = 1) -> list[Move]:
        """Return nearby empty cells on large boards; all moves on 3x3."""
        legal = self.legal_moves()
        # Bàn trống chỉ cần xét ô giữa; bàn 3x3 đủ nhỏ để xét mọi ô.
        if self.size <= 3 or len(legal) == self.size * self.size:
            if len(legal) == self.size * self.size:
                center = self.size // 2
                return [(center, center)]
            return legal
        occupied = [divmod(i, self.size) for i, v in enumerate(self.cells) if v != EMPTY]  # type: ignore[arg-type]
        candidates: set[Move] = set()
        # Trên bàn lớn, giới hạn nước đi quanh các quân đã đánh để giảm phân nhánh.
        for row, col in occupied:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and self.at((nr, nc)) == EMPTY:
                        candidates.add((nr, nc))
        return sorted(candidates) if candidates else legal

    def play(self, move: Move) -> Board:
        row, col = move
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise ValueError(f"move out of bounds: {move}")
        idx = row * self.size + col
        if self.cells[idx] != EMPTY:  # type: ignore[index]
            raise ValueError(f"cell is occupied: {move}")
        cells = list(self.cells)  # type: ignore[arg-type]
        cells[idx] = self.current_player
        return Board(
            size=self.size,
            win_length=self.win_length,
            cells=tuple(cells),
            current_player=self.other(self.current_player),
            last_move=move,
        )

    def winner(self) -> str | None:
        # Sau một nước đi, chỉ cần kiểm tra các đường đi qua ô vừa đánh.
        if self.last_move is not None:
            player = self.at(self.last_move)
            if player != EMPTY and self._wins_through(self.last_move, player):
                return player
            return None
        for move in self.occupied_moves():
            player = self.at(move)
            if self._wins_through(move, player):
                return player
        return None

    def _wins_through(self, move: Move, player: str) -> bool:
        # Đếm hai phía trên bốn hướng: dọc, ngang và hai đường chéo.
        for dr, dc in ((1, 0), (0, 1), (1, 1), (1, -1)):
            count = 1
            for sign in (-1, 1):
                row, col = move
                while True:
                    row += sign * dr
                    col += sign * dc
                    if not (0 <= row < self.size and 0 <= col < self.size):
                        break
                    if self.at((row, col)) != player:
                        break
                    count += 1
            if count >= self.win_length:
                return True
        return False

    def occupied_moves(self) -> Iterator[Move]:
        for i, value in enumerate(self.cells):  # type: ignore[arg-type]
            if value != EMPTY:
                yield divmod(i, self.size)

    def is_full(self) -> bool:
        return EMPTY not in self.cells  # type: ignore[operator]

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.is_full()

    def result_for(self, player: str) -> float:
        winner = self.winner()
        if winner == player:
            return 1.0
        if winner is None:
            return 0.5
        return 0.0

    @classmethod
    def from_rows(cls, rows: Iterable[str], current_player: str = "X", win_length: int | None = None) -> Board:
        normalized = tuple(row.replace(" ", "") for row in rows)
        size = len(normalized)
        if any(len(row) != size for row in normalized):
            raise ValueError("rows must form a square board")
        return cls(size, win_length or size, tuple("".join(normalized)), current_player)

    def __str__(self) -> str:
        width = len(str(self.size - 1))
        header = " " * (width + 1) + " ".join(f"{c:>{width}}" for c in range(self.size))
        rows = [header]
        for r in range(self.size):
            values = " ".join(f"{self.at((r, c)):>{width}}" for c in range(self.size))
            rows.append(f"{r:>{width}} {values}")
        return "\n".join(rows)

