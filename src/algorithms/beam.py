from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS, DEFAULT_BEAM_WIDTH
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class BeamSearch(BaseSearchAlgorithm):
    def __init__(self, beam_width: int = DEFAULT_BEAM_WIDTH):
        super().__init__(f"Beam Search (W={beam_width})")
        self.beam_width = beam_width

    def heuristic(self, grid: WordSearchGrid, row: int, col: int, word: str, index: int) -> int:
        remaining = len(word) - 1 - index
        if index == len(word) - 1:
            return 0

        next_letter = word[index + 1]
        neighbour_matches = sum(
            1 for nr, nc in grid.neighbours(row, col)
            if grid.get_letter(nr, nc) == next_letter
        )

        penalty = 0 if neighbour_matches > 0 else 5
        return remaining + penalty

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        beam = []
        for row, col in grid.positions_of_letter(word[0]):
            beam.append((row, col, 0, [(row, col)]))
            metrics.states_generated += 1

        metrics.max_frontier_size = len(beam)

        while beam:
            metrics.max_frontier_size = max(metrics.max_frontier_size, len(beam))
            candidates = []

            for row, col, index, path in beam:
                if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                    metrics.terminated_early = True
                    break

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
                        score = self.heuristic(grid, nr, nc, word, next_index)
                        candidates.append((score, nr, nc, next_index, new_path))
                        metrics.states_generated += 1

            if metrics.terminated_early:
                break

            candidates.sort(key=lambda x: x[0])
            beam = [(r, c, idx, p) for _, r, c, idx, p in candidates[:self.beam_width]]

        metrics.stop_timer()
        return None, metrics