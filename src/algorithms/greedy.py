import heapq
from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class GreedyBestFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("Greedy Best-First")

    def heuristic(self, grid: WordSearchGrid, row: int, col: int, word: str, index: int) -> int:
        # Calculate number of letters required
        remaining = len(word) - 1 - index
        # Return 0 fi final letter reached
        if index == len(word) - 1:
            return 0

        # Get next target letter
        next_letter = word[index + 1]
        # Count neighbouring cells that match next target letter
        neighbour_matches = sum(
            1 for nr, nc in grid.neighbours(row, col)
            if grid.get_letter(nr, nc) == next_letter
        )

        # Apply penalty if no match exists
        penalty = 0 if neighbour_matches > 0 else 5
        # Lower scores are explored first
        return remaining + penalty

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        # Metrics for performance tracking
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        # Store paths by heuristic score
        frontier = []
        # Keep heap ordering stable when scores are equal
        counter = 0

        # Add all valid starting places to frontier
        for row, col in grid.positions_of_letter(word[0]):
            h = self.heuristic(grid, row, col, word, 0)
            heapq.heappush(frontier, (h, counter, row, col, 0, [(row, col)]))
            counter += 1
            metrics.states_generated += 1

        # Recird initial frontier size
        metrics.max_frontier_size = len(frontier)

        while frontier:
            # Stop searching if node limit is reached
            if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                metrics.terminated_early = True
                break
            
            # Update max frontier size reached
            metrics.max_frontier_size = max(metrics.max_frontier_size, len(frontier))
            # Select most promising path
            _, _, row, col, index, path = heapq.heappop(frontier)
            metrics.nodes_expanded += 1

            # Check if complete word is found
            if index == len(word) - 1:
                metrics.success = True
                metrics.path_length = len(path)
                metrics.stop_timer()
                return path, metrics

            # Move to next letter index
            next_index = index + 1
            # Explore neighbouring cells
            for nr, nc in grid.neighbours(row, col):
                # Continue if next letter matches
                if grid.get_letter(nr, nc) == word[next_index]:
                    # Create updated search path
                    new_path = path + [(nr, nc)]
                    # Calculate heurisitc score for new path
                    h = self.heuristic(grid, nr, nc, word, next_index)
                    # Add new path to frontier
                    heapq.heappush(frontier, (h, counter, nr, nc, next_index, new_path))
                    # Increment counter for stable ordering
                    counter += 1
                    # Increment generated states count
                    metrics.states_generated += 1

        metrics.stop_timer()
        return None, metrics