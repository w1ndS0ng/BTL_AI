from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean

from .board import Board
from .game import play_game
from .mcts import MCTS, MCTSConfig
from .minimax import MinimaxAgent, MinimaxConfig
from .players import RandomPlayer


def run_match_series(games: int, iterations: int, c: float, rollout: str, seed: int) -> dict:
    outcomes: Counter[str] = Counter()
    durations: list[float] = []
    for game_index in range(games):
        mcts = MCTS(MCTSConfig(iterations, c, rollout, seed + game_index))
        random_player = RandomPlayer(seed + 10_000 + game_index)
        # Đổi lượt đi trước sau mỗi ván để giảm thiên lệch của kết quả.
        if game_index % 2 == 0:
            result = play_game(mcts, random_player, Board(3, 3))
            outcome = "win" if result.winner == "X" else "draw" if result.winner is None else "loss"
        else:
            result = play_game(random_player, mcts, Board(3, 3))
            outcome = "win" if result.winner == "O" else "draw" if result.winner is None else "loss"
        outcomes[outcome] += 1
        durations.append(result.duration_seconds)
    return {
        "c": c,
        "iterations": iterations,
        "rollout": rollout,
        "games": games,
        "wins": outcomes["win"],
        "draws": outcomes["draw"],
        "losses": outcomes["loss"],
        "win_rate": outcomes["win"] / games,
        "non_loss_rate": (outcomes["win"] + outcomes["draw"]) / games,
        "avg_seconds": mean(durations),
    }


def minimax_node_comparison() -> list[dict]:
    rows = []
    board = Board(3, 3)
    # Chạy cùng một trạng thái để đo tác dụng riêng của Alpha-Beta.
    for enabled in (False, True):
        agent = MinimaxAgent(MinimaxConfig(alpha_beta=enabled))
        agent.choose_move(board)
        rows.append({"alpha_beta": enabled, "nodes": agent.stats.nodes, "cutoffs": agent.stats.cutoffs})
    return rows


def root_stats(iterations: int, c: float, seed: int) -> list[dict]:
    agent = MCTS(MCTSConfig(iterations, c, "heuristic", seed))
    agent.choose_move(Board(3, 3))
    return [
        {"move": str(row["move"]), "W": row["W"], "N": row["N"], "W/N": row["W/N"]}
        for row in agent.root_statistics()
    ]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_results(rows: list[dict], output: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    # Mỗi giá trị c là một đường trên đồ thị iteration - tỷ lệ thắng.
    for c in sorted({row["c"] for row in rows}):
        selected = sorted(
            (row for row in rows if row["c"] == c and row["rollout"] == "heuristic"),
            key=lambda row: row["iterations"],
        )
        plt.plot([row["iterations"] for row in selected], [row["win_rate"] for row in selected], marker="o", label=f"c={c}")
    plt.xlabel("Số iteration")
    plt.ylabel("Tỷ lệ thắng")
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output, dpi=180)
    plt.close()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Assignment 1 experiments")
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--iterations", type=int, nargs="+", default=[100, 500, 1000, 2000, 5000])
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.5, 1.0, 1.4, 2.0])
    parser.add_argument("--rollouts", nargs="+", choices=["random", "heuristic"], default=["random", "heuristic"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    if args.quick:
        args.games, args.iterations, args.c_values = 6, [50, 150], [1.0, 1.4]
    args.output.mkdir(parents=True, exist_ok=True)

    sweep = [
        run_match_series(args.games, iterations, c, rollout, args.seed)
        for rollout in args.rollouts
        for c in args.c_values
        for iterations in args.iterations
    ]
    nodes = minimax_node_comparison()
    stats = root_stats(max(args.iterations), 1.4, args.seed)
    write_csv(args.output / "mcts_sweep.csv", sweep)
    write_csv(args.output / "minimax_nodes.csv", nodes)
    write_csv(args.output / "root_stats.csv", stats)
    plotted = plot_results(sweep, args.output / "win_rate.png")
    summary = {"configuration": vars(args) | {"output": str(args.output)}, "mcts": sweep, "minimax": nodes, "plot_created": plotted}
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Results written to {args.output.resolve()}")


if __name__ == "__main__":
    main()

