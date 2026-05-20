from typing import List, Tuple

Position = Tuple[int, int]

class WordSearchGrid:
    def __init__(self, grid: List[List[str]]):
        # Store grid in uppercase 
        self.grid = [[cell.upper() for cell in row] for row in grid]

        # Number of rows and columns
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0

    def in_bounds(self, row: int, col: int) -> bool:
        # Check if position is inside grid boundaries
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_letter(self, row: int, col: int) -> str:
        # Return letter at specific grid position
        return self.grid[row][col]

    def neighbours(self, row: int, col: int) -> List[Position]:
        # Define 8 possible directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        # Store valid neighbouring positions
        result = []

        # Check all possible neighbouring directions
        for dr, dc in directions:
            nr, nc = row + dr, col + dc

            # Add neighbour only if it is inside grid
            if self.in_bounds(nr, nc):
                result.append((nr, nc))

        return result

    def positions_of_letter(self, letter: str) -> List[Position]:
        # Store matching positions
        matches = []

        # Search all cells in grid
        for r in range(self.rows):
            for c in range(self.cols):
                # Check if current cell matches target letter
                if self.grid[r][c] == letter.upper():
                    matches.append((r, c))

        return matches

    def display(self) -> None:
        # Print grid row by row
        for row in self.grid:
            print(" ".join(row))