from __future__ import annotations

import argparse

from .board import Board
from .game import play_game
from .mcts import MCTS, MCTSConfig
from .minimax import MinimaxAgent, MinimaxConfig
from .players import HumanPlayer, RandomPlayer


def build_player(name: str, args: argparse.Namespace, seed_offset: int = 0):
    if name == "human":
        return HumanPlayer()
    if name == "random":
        return RandomPlayer(args.seed + seed_offset)
    if name == "minimax":
        return MinimaxAgent(MinimaxConfig(max_depth=args.depth, alpha_beta=True))
    return MCTS(
        MCTSConfig(
            iterations=args.iterations,
            exploration_c=args.c,
            rollout=args.rollout,
            seed=args.seed + seed_offset,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generalized Tic-Tac-Toe")
    parser.add_argument("--x", choices=["human", "random", "minimax", "mcts"], default="human")
    parser.add_argument("--o", choices=["human", "random", "minimax", "mcts"], default="mcts")
    parser.add_argument("--size", type=int, default=9)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--depth", type=int, default=None)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--c", type=float, default=1.4)
    parser.add_argument("--rollout", choices=["random", "heuristic"], default="heuristic")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    result = play_game(
        build_player(args.x, args),
        build_player(args.o, args, 1),
        Board(args.size, args.win_length),
        verbose=True,
    )
    print(f"Result: {result.winner or 'draw'}; {result.moves} moves; {result.duration_seconds:.3f}s")


if __name__ == "__main__":
    main()

