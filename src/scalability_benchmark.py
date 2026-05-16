import os
import pandas as pd

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.puzzle_generator import PuzzleGenerator


class ScalabilityBenchmark:
    def __init__(self):
        self.runner = BenchmarkRunner()

    def run(self, grid_sizes, words, repetitions: int = 3) -> pd.DataFrame:
        all_results = []

        for size in grid_sizes:
            for repetition in range(1, repetitions + 1):
                print(f"\nRunning benchmark: {size}x{size}, repetition {repetition}")

                generator = PuzzleGenerator(rows=size, cols=size, allow_diagonal=True)
                grid_data, placements = generator.generate(words)

                grid = WordSearchGrid(grid_data)
                df = self.runner.run(grid, words)

                df["grid_size"] = size
                df["repetition"] = repetition

                all_results.append(df)

        final_df = pd.concat(all_results, ignore_index=True)

        os.makedirs("results", exist_ok=True)
        final_df.to_csv("results/scalability_results.csv", index=False)

        return final_df