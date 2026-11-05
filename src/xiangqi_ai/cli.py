"""Chạy thử AI bằng terminal, không phụ thuộc thư viện giao diện."""
import argparse
import json
from .board import Board
from .minimax import MinimaxAgent
from .mcts import MCTS


def main():
    parser = argparse.ArgumentParser(description="Xiangqi AI demonstration")
    parser.add_argument("--red", choices=("minimax", "mcts"), default="minimax")
    parser.add_argument("--black", choices=("minimax", "mcts"), default="mcts")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--c", type=float, default=1.4)
    parser.add_argument("--rollout", choices=("random", "heuristic"), default="heuristic")
    parser.add_argument("--rollout-steps", type=int, default=20)
    parser.add_argument("--max-plies", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.max_plies < 1:
        parser.error("max-plies must be positive")
    agents = {side: MinimaxAgent(args.depth) if name == "minimax" else
              MCTS(args.iterations, args.c, args.rollout, args.seed + i, args.rollout_steps)
              for i, (side, name) in enumerate((("red", args.red), ("black", args.black)))}
    board = Board()
    print(board)
    for ply in range(args.max_plies):
        winner = board.winner()
        if winner:
            break
        move = agents[board.current_player].choose_move(board)
        print(f"{ply + 1}: {board.current_player} {move}")
        board = board.play(move)
    print(board)
    print(json.dumps({"winner": board.winner(), "status": "finished" if board.winner() else "move_limit"}))


if __name__ == "__main__":
    main()
