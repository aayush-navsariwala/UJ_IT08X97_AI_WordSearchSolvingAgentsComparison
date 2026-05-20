import random
import string
from typing import List, Tuple, Optional

Position = Tuple[int, int]

class PuzzleGenerator:
    def __init__(self, rows: int, cols: int, allow_diagonal: bool = True):
        # Store grid dimensions
        self.rows = rows
        self.cols = cols

        # Store if diagonal word placement is allowed
        self.allow_diagonal = allow_diagonal

        # Create empty grid
        self.grid = [["" for _ in range(cols)] for _ in range(rows)]

        # Define movement directions
        self.directions = [
            # right
            (0, 1),    
            # left
            (0, -1),   
            # down
            (1, 0),    
            # up
            (-1, 0),   
        ]

        # Add diagonal directions  
        if allow_diagonal:
            self.directions.extend([
                # down right
                (1, 1),     
                # down left
                (1, -1),    
                # up right
                (-1, 1),    
                # up left
                (-1, -1),   
            ])

    def can_place_word(self, word: str, row: int, col: int, dr: int, dc: int) -> bool:
        # Check if word can fit from starting position
        for i, letter in enumerate(word):
            nr = row + i * dr
            nc = col + i * dc

            # Reject placement if position leaves grid
            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                return False

            # Get current grid value at target position
            current = self.grid[nr][nc]

            # Reject placement if existing letter conflicts
            if current != "" and current != letter:
                return False

        return True

    def place_word(self, word: str) -> Optional[List[Position]]:
        # Convert word to uppercase 
        word = word.upper()

        # Limit placement attempts to avoid infinite loop
        attempts = 200

        # Try random placements until valid one is found
        for _ in range(attempts):
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            dr, dc = random.choice(self.directions)

            # Place word if selected position and direction are valid
            if self.can_place_word(word, row, col, dr, dc):
                path = []

                # Write each letter of word into grid
                for i, letter in enumerate(word):
                    nr = row + i * dr
                    nc = col + i * dc
                    self.grid[nr][nc] = letter
                    path.append((nr, nc))

                return path

        return None

    def fill_empty_cells(self):
        # Fill all remaining empty cells with random uppercase letters
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "":
                    self.grid[r][c] = random.choice(string.ascii_uppercase)

    def generate(self, words: List[str]) -> Tuple[List[List[str]], dict]:
        # Store placed path for each word
        placements = {}

        # Attempt to place each target word in grid
        for word in words:
            path = self.place_word(word)
            placements[word.upper()] = path

        # Fill unused cells after placing target words
        self.fill_empty_cells()

        return self.grid, placements