import os

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.visualiser import ResultVisualiser
from src.puzzle_generator import PuzzleGenerator


def main():
    words = ["CAT", "DOG", "BIRD", "FISH", "HOUSE"]

    generator = PuzzleGenerator(rows=10, cols=10, allow_diagonal=True)
    grid_data, placements = generator.generate(words)

    print("Generated Word Search:")
    grid = WordSearchGrid(grid_data)
    grid.display()

    print("\nWord Placements:")
    for word, path in placements.items():
        print(f"{word}: {path}")

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