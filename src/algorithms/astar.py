import heapq
from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class AStarSearch(BaseSearchAlgorithm):
    def __init__(self):
        # Set the name of the algorithm
        super().__init__("A*")

    def heuristic(self, grid: WordSearchGrid, row: int, col: int, word: str, index: int) -> int:
        # Calculate how many letters remain to be matched
        remaining = len(word) - 1 - index
        # Return 0 if the full word has been matched
        if index == len(word) - 1:
            return 0

        # Get the next required letter
        next_letter = word[index + 1]
        # Count neighbouring cells with next letter
        neighbour_matches = sum(
            1 for nr, nc in grid.neighbours(row, col)
            if grid.get_letter(nr, nc) == next_letter
        )

        # Add penalty if no matching neighbour exists
        penalty = 0 if neighbour_matches > 0 else 3
        # Return heuristic score
        return remaining + penalty

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        # Convert target word to uppercase
        word = word.upper()
        # Create the metrics tracker
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        # Start timing the search
        metrics.start_timer()
        # Priority queue used as frontier
        frontier = []
        # Counter to maintain queue order
        counter = 0
        
        # Add all starting positions matching the first letter
        for row, col in grid.positions_of_letter(word[0]):
            g = 0
            h = self.heuristic(grid, row, col, word, 0)
            f = g + h
            
            # Add starting state to frontier
            heapq.heappush(frontier, (f, counter, row, col, 0, [(row, col)]))
            counter += 1
            metrics.states_generated += 1

        # Store initial frontier size
        metrics.max_frontier_size = len(frontier)

        # Continue searchine while states in frontier
        while frontier:
            # Stop search if node expansion limit is reached
            if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                metrics.terminated_early = True
                break
            
            # Track largest frontier size reached
            metrics.max_frontier_size = max(metrics.max_frontier_size, len(frontier))
            # Remove state with lowest f score
            _, _, row, col, index, path = heapq.heappop(frontier)
            # Increment expanded node count
            metrics.nodes_expanded += 1

            # Check if full word is matched
            if index == len(word) - 1:
                metrics.success = True
                metrics.path_length = len(path)
                metrics.stop_timer()
                return path, metrics

            # Move to next letter index
            next_index = index + 1
            # Search neighbouring cells
            for nr, nc in grid.neighbours(row, col):
                if grid.get_letter(nr, nc) == word[next_index]:
                    new_path = path + [(nr, nc)]
                    # Calculate cost and heuristic values
                    g = next_index
                    h = self.heuristic(grid, nr, nc, word, next_index)
                    f = g + h
                    # Add new state to frontier
                    heapq.heappush(frontier, (f, counter, nr, nc, next_index, new_path))
                    counter += 1
                    metrics.states_generated += 1

        # Stop timer if no solution
        metrics.stop_timer()
        return None, metrics