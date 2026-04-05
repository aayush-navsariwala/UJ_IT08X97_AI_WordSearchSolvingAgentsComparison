from typing import List, Tuple, Optional, Set

from src.algorithms.base import BaseSearchAlgorithm
from src. grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class DepthFirstSearch(BaseSearchAlgorithm):
    def __init__(self):
        super().__init__("DFS")
        
    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        def dfs(row: int, col: int, index: int, path: List[Position], visited: Set[Position]) -> Optional[List[Position]]:
            metrics.nodes_expanded += 1

            if grid.get_letter(row, col) != word[index]:
                return None

            path = path + [(row, col)]
            visited = visited | {(row, col)}

            if index == len(word) - 1:
                return path

            for nr, nc in grid.neighbours(row, col):
                metrics.states_generated += 1
                if (nr, nc) not in visited:
                    result = dfs(nr, nc, index + 1, path, visited)
                    if result is not None:
                        return result

            return None

        result_path = None
        start_positions = grid.positions_of_letter(word[0])

        for row, col in start_positions:
            result_path = dfs(row, col, 0, [], set())
            if result_path is not None:
                break

        metrics.success = result_path is not None
        metrics.path_length = len(result_path) if result_path else 0
        metrics.stop_timer()

        return result_path, metrics