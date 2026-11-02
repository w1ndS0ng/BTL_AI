from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from .board import Board, Move


class Player(Protocol):
    def choose_move(self, board: Board) -> Move: ...


@dataclass(slots=True)
class GameResult:
    winner: str | None
    moves: int
    duration_seconds: float
    final_board: Board


def play_game(x_player: Player, o_player: Player, board: Board | None = None, verbose: bool = False) -> GameResult:
    state = board or Board()
    players = {"X": x_player, "O": o_player}
    move_count = 0
    started = perf_counter()
    # Hai tác nhân luân phiên chọn nước cho đến khi thắng hoặc hết ô.
    while not state.is_terminal():
        if verbose:
            print(state, "\n")
        move = players[state.current_player].choose_move(state)
        state = state.play(move)
        move_count += 1
    if verbose:
        print(state)
    return GameResult(state.winner(), move_count, perf_counter() - started, state)

