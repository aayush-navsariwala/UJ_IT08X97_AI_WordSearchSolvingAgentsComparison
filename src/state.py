from dataclasses import dataclass, field
from typing import List, Set, Tuple

Position = Tuple[int, int]

@dataclass
class SearchState:
    row: int
    col: int
    word_index: int
    path: List[Position] = field(default_factory=list)
    visited: Set[Position] = field(default_factory=set)
    
    def current_position(self) -> Position:
        return (self.row, self.col)