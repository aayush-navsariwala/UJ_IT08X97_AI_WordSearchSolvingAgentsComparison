import os
import pandas as pd

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.puzzle_generator import PuzzleGenerator

class ScalabilityBenchmark:
    def __init__(self):
        # Create benchmark runner used for all scalability tests
        self.runner = BenchmarkRunner()

    def run(self, grid_sizes, words, repetitions: int = 3) -> pd.DataFrame:
        # Store benchmark results from all experiments
        all_results = []

        # Test every grid size
        for size in grid_sizes:
            # Repeat every grid size multiple times
            for repetition in range(1, repetitions + 1):
                # Display current benchmark progress
                print(f"\nRunning benchmark: {size}x{size}, repetition {repetition}")

                # Generate new puzzle grid
                generator = PuzzleGenerator(rows=size, cols=size, allow_diagonal=True)
                grid_data, placements = generator.generate(words)

                # Create grid object used by search algorithms
                grid = WordSearchGrid(grid_data)

                # Run all algorithms on generated puzzle
                df = self.runner.run(grid, words)

                # Store current grid size in results
                df["grid_size"] = size

                # Store current repetition number
                df["repetition"] = repetition

                # Add results to the dataset
                all_results.append(df)

        # Combine all benchmark results into single dataframe
        final_df = pd.concat(all_results, ignore_index=True)

        # Create results directory if it does not exist
        os.makedirs("results", exist_ok=True)

        # Save scalability benchmark results to CSV file
        final_df.to_csv("results/scalability_results.csv", index=False)

        return final_df