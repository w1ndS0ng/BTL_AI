from __future__ import annotations

import argparse
from collections import Counter

from .board import Board
from .game import play_game
from .mcts import MCTS, MCTSConfig
from .minimax import MinimaxAgent, MinimaxConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Empirically validate that MCTS does not lose on 3x3")
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--iterations", type=int, default=3000)
    parser.add_argument("--c", type=float, default=1.4)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    outcomes: Counter[str] = Counter()
    # MCTS lần lượt đi trước và đi sau khi đấu với Minimax tối ưu.
    for index in range(args.games):
        mcts = MCTS(MCTSConfig(args.iterations, args.c, "heuristic", args.seed + index))
        optimal = MinimaxAgent(MinimaxConfig())
        if index % 2 == 0:
            result = play_game(mcts, optimal, Board(3, 3))
            outcome = "win" if result.winner == "X" else "draw" if result.winner is None else "loss"
        else:
            result = play_game(optimal, mcts, Board(3, 3))
            outcome = "win" if result.winner == "O" else "draw" if result.winner is None else "loss"
        outcomes[outcome] += 1
    print(dict(outcomes))
    if outcomes["loss"]:
        raise SystemExit("MCTS lost at least one game; increase iterations or tune rollout/c.")
    print("PASS: no loss observed against optimal Minimax.")


if __name__ == "__main__":
    main()

