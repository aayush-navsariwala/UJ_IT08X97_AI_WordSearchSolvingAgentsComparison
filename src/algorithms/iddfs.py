from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class IterativeDeepeningDFS(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("IDDFS")

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        # Convert words to uppercase
        word = word.upper()

        # Metrics for performance tracking
        metrics = SearchMetrics(algorithm_name=self.name, word=word)

        metrics.start_timer()

        def depth_limited_dfs(
            row: int,
            col: int,
            index: int,
            depth_limit: int,
            path: List[Position]
        ) -> Optional[List[Position]]:
            # Stop search if node expansion limit reached
            if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                metrics.terminated_early = True
                return None

            # Increment expanded node count
            metrics.nodes_expanded += 1

            # Stop path if current letter does not match
            if grid.get_letter(row, col) != word[index]:
                return None

            # Add current cell to search path
            new_path = path + [(row, col)]

            # Return path if full word found
            if index == len(word) - 1:
                return new_path

            # Stop expanding path if the depth limit reached
            if len(new_path) >= depth_limit:
                return None

            # Search neighbouring cells with current depth limit
            for nr, nc in grid.neighbours(row, col):
                metrics.states_generated += 1
                result = depth_limited_dfs(nr, nc, index + 1, depth_limit, new_path)

                # Return when valid path found
                if result is not None:
                    return result

            return None
        
        result_path = None

        # Find grid cell that matches first letter
        start_positions = grid.positions_of_letter(word[0])

        # Increase search depth one level 
        for depth_limit in range(1, len(word) + 1):
            # Start depth limited search from each starting position
            for row, col in start_positions:
                result_path = depth_limited_dfs(row, col, 0, depth_limit, [])

                # Stop when solution found or the search limit  reached
                if result_path is not None or metrics.terminated_early:
                    break

            # Stop increasing depth if result or limit condition reached
            if result_path is not None or metrics.terminated_early:
                break

        # Record success or not
        metrics.success = result_path is not None

        # Record length of discovered path
        metrics.path_length = len(result_path) if result_path else 0

        metrics.stop_timer()

        return result_path, metrics