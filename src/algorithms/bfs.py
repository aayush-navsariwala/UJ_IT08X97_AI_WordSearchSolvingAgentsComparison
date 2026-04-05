from collections import deque
from typing import List, Tuple, Optional, Set

from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]


class BreadthFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("BFS")

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        queue = deque()

        for row, col in grid.positions_of_letter(word[0]):
            queue.append((row, col, 0, [(row, col)], {(row, col)}))
            metrics.states_generated += 1

        metrics.max_frontier_size = len(queue)

        while queue:
            metrics.max_frontier_size = max(metrics.max_frontier_size, len(queue))
            row, col, index, path, visited = queue.popleft()
            metrics.nodes_expanded += 1

            if index == len(word) - 1:
                metrics.success = True
                metrics.path_length = len(path)
                metrics.stop_timer()
                return path, metrics

            for nr, nc in grid.neighbours(row, col):
                if (nr, nc) not in visited and grid.get_letter(nr, nc) == word[index + 1]:
                    new_path = path + [(nr, nc)]
                    new_visited = visited | {(nr, nc)}
                    queue.append((nr, nc, index + 1, new_path, new_visited))
                    metrics.states_generated += 1

        metrics.stop_timer()
        return None, metrics