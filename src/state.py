from dataclasses import dataclass, field
from typing import List, Set, Tuple

Position = Tuple[int, int]

@dataclass
class SearchState:
    # Store row position
    row: int

    # Store column position
    col: int

    # Store index within target word
    word_index: int

    # Store path taken through grid
    path: List[Position] = field(default_factory=list)

    def current_position(self) -> Position:
        # Return current grid position as tuple
        return (self.row, self.col)