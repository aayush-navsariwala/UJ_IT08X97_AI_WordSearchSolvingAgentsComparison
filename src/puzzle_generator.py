import random
import string
from typing import List, Tuple, Optional


Position = Tuple[int, int]


class PuzzleGenerator:
    def __init__(self, rows: int, cols: int, allow_diagonal: bool = True):
        self.rows = rows
        self.cols = cols
        self.allow_diagonal = allow_diagonal
        self.grid = [["" for _ in range(cols)] for _ in range(rows)]

        self.directions = [
            (0, 1),    # right
            (0, -1),   # left
            (1, 0),    # down
            (-1, 0),   # up
        ]

        if allow_diagonal:
            self.directions.extend([
                (1, 1),     # down-right
                (1, -1),    # down-left
                (-1, 1),    # up-right
                (-1, -1),   # up-left
            ])

    def can_place_word(self, word: str, row: int, col: int, dr: int, dc: int) -> bool:
        for i, letter in enumerate(word):
            nr = row + i * dr
            nc = col + i * dc

            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                return False

            current = self.grid[nr][nc]

            if current != "" and current != letter:
                return False

        return True

    def place_word(self, word: str) -> Optional[List[Position]]:
        word = word.upper()
        attempts = 200

        for _ in range(attempts):
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            dr, dc = random.choice(self.directions)

            if self.can_place_word(word, row, col, dr, dc):
                path = []

                for i, letter in enumerate(word):
                    nr = row + i * dr
                    nc = col + i * dc
                    self.grid[nr][nc] = letter
                    path.append((nr, nc))

                return path

        return None

    def fill_empty_cells(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "":
                    self.grid[r][c] = random.choice(string.ascii_uppercase)

    def generate(self, words: List[str]) -> Tuple[List[List[str]], dict]:
        placements = {}

        for word in words:
            path = self.place_word(word)
            placements[word.upper()] = path

        self.fill_empty_cells()
        return self.grid, placements