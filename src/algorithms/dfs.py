from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class DepthFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("DFS")

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        # Convert to uppercase
        word = word.upper()
        # Create metrics for performance tracking
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        def dfs(row: int, col: int, index: int, path: List[Position]) -> Optional[List[Position]]:
            # Stop search if node limit reached
            if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                metrics.terminated_early = True
                return None

            metrics.nodes_expanded += 1

            # Stop path if current letter does not match
            if grid.get_letter(row, col) != word[index]:
                return None

            # Add current cell to search path
            new_path = path + [(row, col)]

            # Return path if full word is found
            if index == len(word) - 1:
                return new_path

            # Explore neighbouring cells with depth first traversal
            for nr, nc in grid.neighbours(row, col):
                metrics.states_generated += 1
                result = dfs(nr, nc, index + 1, new_path)
                # Return if valid path is found
                if result is not None:
                    return result

            return None

        # Store final path is solution is found
        result_path = None
        # Find every grid cell that matches first letter
        start_positions = grid.positions_of_letter(word[0])

        # Start DFS from every possible starting place
        for row, col in start_positions:
            result_path = dfs(row, col, 0, [])
            # Stop when solution found or search limit reached
            if result_path is not None or metrics.terminated_early:
                break

        # Record if search succeeded
        metrics.success = result_path is not None
        # Record length of found path
        metrics.path_length = len(result_path) if result_path else 0
        metrics.stop_timer()
        return result_path, metrics