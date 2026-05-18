from collections import deque
from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class BreadthFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("BFS")

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        # Create metrics for performance tracking
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        # Create BFS queue
        queue = deque()

        # Add valid starting positions to queue
        for row, col in grid.positions_of_letter(word[0]):
            queue.append((row, col, 0, [(row, col)]))
            metrics.states_generated += 1

        # Record initial frontier size
        metrics.max_frontier_size = len(queue)

        # Continue searching while paths in queue
        while queue:
            # Stop search if node expansion limit reached
            if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                metrics.terminated_early = True
                break
            
            # Update maximum frontier size reached
            metrics.max_frontier_size = max(metrics.max_frontier_size, len(queue))
            # Remove next path from queue
            row, col, index, path = queue.popleft()
            # Increment expanded node count
            metrics.nodes_expanded += 1

            # Check if full word is found
            if index == len(word) - 1:
                metrics.success = True
                metrics.path_length = len(path)
                metrics.stop_timer()
                return path, metrics

            # Explore neighbouring cells
            for nr, nc in grid.neighbours(row, col):
                # Continue only if next letter matches
                if grid.get_letter(nr, nc) == word[index + 1]:
                    # Create updated path
                    new_path = path + [(nr, nc)]
                    # Add new state to queue
                    queue.append((nr, nc, index + 1, new_path))
                    # Increment generated state count
                    metrics.states_generated += 1

        metrics.stop_timer()
        return None, metrics