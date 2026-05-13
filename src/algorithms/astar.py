import heapq
from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]


class AStarSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("A*")

    def heuristic(self, grid: WordSearchGrid, row: int, col: int, word: str, index: int) -> int:
        remaining = len(word) - 1 - index
        if index == len(word) - 1:
            return 0

        next_letter = word[index + 1]
        neighbour_matches = sum(
            1 for nr, nc in grid.neighbours(row, col)
            if grid.get_letter(nr, nc) == next_letter
        )

        penalty = 0 if neighbour_matches > 0 else 3
        return remaining + penalty

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        frontier = []
        counter = 0

        for row, col in grid.positions_of_letter(word[0]):
            g = 0
            h = self.heuristic(grid, row, col, word, 0)
            f = g + h
            heapq.heappush(frontier, (f, counter, row, col, 0, [(row, col)]))
            counter += 1
            metrics.states_generated += 1

        metrics.max_frontier_size = len(frontier)

        while frontier:
            if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                metrics.terminated_early = True
                break

            metrics.max_frontier_size = max(metrics.max_frontier_size, len(frontier))
            _, _, row, col, index, path = heapq.heappop(frontier)
            metrics.nodes_expanded += 1

            if index == len(word) - 1:
                metrics.success = True
                metrics.path_length = len(path)
                metrics.stop_timer()
                return path, metrics

            next_index = index + 1
            for nr, nc in grid.neighbours(row, col):
                if grid.get_letter(nr, nc) == word[next_index]:
                    new_path = path + [(nr, nc)]
                    g = next_index
                    h = self.heuristic(grid, nr, nc, word, next_index)
                    f = g + h
                    heapq.heappush(frontier, (f, counter, nr, nc, next_index, new_path))
                    counter += 1
                    metrics.states_generated += 1

        metrics.stop_timer()
        return None, metrics