import time
from dataclasses import dataclass

@dataclass
class SearchMetrics:
    algorithm_name: str
    word: str
    execution_time_ms: float = 0.0
    nodes_expanded: int = 0
    states_generated: int = 0
    max_frontier_size: int = 0
    success: bool = False
    path_length: int = 0
    MAX_NODE_EXPANSIONS = 200000
    
    def start_timer(self):
        self._start = time.perf_counter()
        
    def stop_timer(self):
        end = time.perf_counter()
        self.execution_time_ms = (end - self._start) * 1000
        