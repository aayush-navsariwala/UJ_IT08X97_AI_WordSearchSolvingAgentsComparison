from typing import List, Tuple

Position = Tuple[int, int]

class WordSearchGrid:
    def __init__(self, grid: List[List[str]]):
        self.grid = [[cell.upper() for cell in row] for row in grid]
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_letter(self, row: int, col: int) -> str:
        return self.grid[row][col]

    def neighbours(self, row: int, col: int) -> List[Position]:
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        result = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if self.in_bounds(nr, nc):
                result.append((nr, nc))
        return result

    def positions_of_letter(self, letter: str) -> List[Position]:
        matches = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == letter.upper():
                    matches.append((r, c))
        return matches

    def display(self) -> None:
        for row in self.grid:
            print(" ".join(row))