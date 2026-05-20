import os

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.visualiser import ResultVisualiser
from src.puzzle_generator import PuzzleGenerator

def main():
    # Define target words used in puzzle
    words = ["CAT", "DOG", "BIRD", "FISH", "HOUSE"]

    # Create random puzzle generator
    generator = PuzzleGenerator(rows=10, cols=10, allow_diagonal=True)

    # Generate puzzle grid and store word placements
    grid_data, placements = generator.generate(words)

    # Display generated word search
    print("Generated Word Search:")

    # Create grid object
    grid = WordSearchGrid(grid_data)

    # Print puzzle grid to console
    grid.display()

    # Display placement path for every word
    print("\nWord Placements:")

    for word, path in placements.items():
        print(f"{word}: {path}")

    # Create benchmark runner
    benchmark = BenchmarkRunner()

    # Run all search algorithms on puzzle
    df = benchmark.run(grid, words)

    # Create results directory if it does not exist
    os.makedirs("results", exist_ok=True)

    # Save benchmark results to CSV file
    df.to_csv("results/benchmark_results.csv", index=False)

    # Create graph visualiser
    visualiser = ResultVisualiser()

    # Generate execution time comparison graph
    visualiser.plot_metric_by_algorithm(df, "execution_time_ms", "time_comparison.png")

    # Generate node expansion comparison graph
    visualiser.plot_metric_by_algorithm(df, "nodes_expanded", "nodes_comparison.png")

    # Generate frontier size comparison graph
    visualiser.plot_metric_by_algorithm(df, "max_frontier_size", "frontier_comparison.png")

    # Generate generated states comparison graph
    visualiser.plot_metric_by_algorithm(df, "states_generated", "generated_states_comparison.png")

    # Display completion message
    print("\nResults saved to results/benchmark_results.csv")

if __name__ == "__main__":
    main()