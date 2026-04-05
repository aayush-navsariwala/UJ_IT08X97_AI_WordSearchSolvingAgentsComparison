import os

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.visualiser import ResultVisualiser

def main():
    grid_data = [
        ["C", "A", "T", "D", "O"],
        ["X", "Z", "O", "G", "G"],
        ["Y", "D", "O", "G", "P"],
        ["B", "I", "R", "D", "Q"],
        ["F", "I", "S", "H", "R"]
    ]

    words = ["CAT", "DOG", "BIRD", "FISH"]

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

    print("\nResults saved to results/benchmark_results.csv")


if __name__ == "__main__":
    main()