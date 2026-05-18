from typing import List, Tuple, Optional

from config import MAX_NODE_EXPANSIONS, DEFAULT_BEAM_WIDTH
from src.algorithms.base import BaseSearchAlgorithm
from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class BeamSearch(BaseSearchAlgorithm):
    def __init__(self, beam_width: int = DEFAULT_BEAM_WIDTH):
        super().__init__(f"Beam Search (W={beam_width})")
        # Store the max number of paths per level
        self.beam_width = beam_width

    def heuristic(self, grid: WordSearchGrid, row: int, col: int, word: str, index: int) -> int:
        # Calculate remaining letters required
        remaining = len(word) - 1 - index
        if index == len(word) - 1:
            return 0

        # Get next target letter
        next_letter = word[index + 1]
        # Count neighbouring cells with next required letter
        neighbour_matches = sum(
            1 for nr, nc in grid.neighbours(row, col)
            if grid.get_letter(nr, nc) == next_letter
        )

        # Add penalty if no neighbouring match exists
        penalty = 0 if neighbour_matches > 0 else 5
        return remaining + penalty

    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        word = word.upper()
        # Metrics object to record performance
        metrics = SearchMetrics(algorithm_name=self.name, word=word)
        metrics.start_timer()

        # Store active paths
        beam = []
        # Add all valid starting positions to the beam
        for row, col in grid.positions_of_letter(word[0]):
            beam.append((row, col, 0, [(row, col)]))
            metrics.states_generated += 1

        # Record initial beam size
        metrics.max_frontier_size = len(beam)

        while beam:
            # Update maximum frontier size reached
            metrics.max_frontier_size = max(metrics.max_frontier_size, len(beam))
            candidates = []

            # Explore each path in beam
            for row, col, index, path in beam:
                # Stop searching if node expansion limit reached
                if metrics.nodes_expanded >= MAX_NODE_EXPANSIONS:
                    metrics.terminated_early = True
                    break
                
                # Increment expanded node count
                metrics.nodes_expanded += 1

                # Check if full word is found
                if index == len(word) - 1:
                    metrics.success = True
                    metrics.path_length = len(path)
                    metrics.stop_timer()
                    return path, metrics

                # Move to next letter index
                next_index = index + 1
                for nr, nc in grid.neighbours(row, col):
                    # Continue if next letter matches
                    if grid.get_letter(nr, nc) == word[next_index]:
                        # Create updated search path 
                        new_path = path + [(nr, nc)]
                        # Calculate heuristic score for new path
                        score = self.heuristic(grid, nr, nc, word, next_index)
                        candidates.append((score, nr, nc, next_index, new_path))
                        # Increment generated state count
                        metrics.states_generated += 1

            if metrics.terminated_early:
                break
            
            # Sort by heuristic score
            candidates.sort(key=lambda x: x[0])
            # Keep best paths within beam width
            beam = [(r, c, idx, p) for _, r, c, idx, p in candidates[:self.beam_width]]

        metrics.stop_timer()
        return None, metrics