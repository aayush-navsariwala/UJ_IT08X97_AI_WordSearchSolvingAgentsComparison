import time
from dataclasses import dataclass

@dataclass
class SearchMetrics:
    # Store algorithm name
    algorithm_name: str

    # Store target word being searched
    word: str

    # Record execution time in milliseconds
    execution_time_ms: float = 0.0

    # Record expanded nodes
    nodes_expanded: int = 0

    # Record generated states
    states_generated: int = 0

    # Record biggest frontier size 
    max_frontier_size: int = 0

    # Record if search succeeded
    success: bool = False

    # Record final path length
    path_length: int = 0

    # Record if search stopped early
    terminated_early: bool = False

    def start_timer(self):
        # Store starting time of the search
        self._start = time.perf_counter()

    def stop_timer(self):
        # Store ending time of the search
        end = time.perf_counter()

        # Calculate execution time
        self.execution_time_ms = (end - self._start) * 1000