import pandas as pd
from typing import List

from src.grid import WordSearchGrid
from src.algorithms.dfs import DepthFirstSearch
from src.algorithms.bfs import BreadthFirstSearch
from src.algorithms.iddfs import IterativeDeepeningDFS
from src.algorithms.greedy import GreedyBestFirstSearch
from src.algorithms.astar import AStarSearch
from src.algorithms.beam import BeamSearch


class BenchmarkRunner:
    def __init__(self):
        # Store algorithms that will be compared
        self.algorithms = [
            DepthFirstSearch(),
            BreadthFirstSearch(),
            IterativeDeepeningDFS(),
            GreedyBestFirstSearch(),
            AStarSearch(),
            BeamSearch(beam_width=3),
        ]

    def run(self, grid: WordSearchGrid, words: List[str]) -> pd.DataFrame:
        # Store every algorithm result as table row
        rows = []

        # Run algorithm against all target words
        for word in words:
            for algorithm in self.algorithms:
                # Execute current algorithm and collect metrics
                path, metrics = algorithm.search(grid, word)

                # Add result to benchmark dataset
                rows.append({
                    "algorithm": metrics.algorithm_name,
                    "word": metrics.word,
                    "success": metrics.success,
                    "execution_time_ms": metrics.execution_time_ms,
                    "nodes_expanded": metrics.nodes_expanded,
                    "states_generated": metrics.states_generated,
                    "max_frontier_size": metrics.max_frontier_size,
                    "path_length": metrics.path_length,
                    "terminated_early": metrics.terminated_early,
                    "path": path if path else []
                })

                # Print summary for debugging
                print(
                    f"{metrics.algorithm_name} | "
                    f"{word} | "
                    f"success={metrics.success} | "
                    f"time={metrics.execution_time_ms:.3f}ms | "
                    f"nodes={metrics.nodes_expanded} | "
                    f"path={path}"
                )

        # Return benchmark results as dataframe
        return pd.DataFrame(rows)