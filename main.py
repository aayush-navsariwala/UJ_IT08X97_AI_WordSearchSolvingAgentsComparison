import os

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.visualiser import ResultVisualiser
from src.manual_input import load_grid_from_lines


def main():
    lines = [
        "CATDO",
        "XZOGG",
        "YDOGP",
        "BIRDQ",
        "FISHR"
    ]

    words = ["CAT", "DOG", "BIRD", "FISH", "GOOD"]

    grid_data = load_grid_from_lines(lines)
    grid = WordSearchGrid(grid_data)
    grid.display()

    benchmark = BenchmarkRunner()
    df = benchmark.run(grid, words)

    os.makedirs("results", exist_ok=True)
    df.to_csv("results/benchmark_results.csv", index=False)

    visualiser = ResultVisualiser()
    visualiser.plot_metric_by_algorithm(df, "execution_time_ms", "time_comparison.png")
    visualiser.plot_metric_by_algorithm(df, "nodes_expanded", "nodes_comparison.png")
    visualiser.plot_metric_by_algorithm(df, "max_frontier_size", "frontier_comparison.png")
    visualiser.plot_metric_by_algorithm(df, "states_generated", "generated_states_comparison.png")

    print("\nResults saved to results/benchmark_results.csv")


if __name__ == "__main__":
    main()