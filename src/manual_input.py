from typing import List

def load_grid_from_lines(lines: List[str]) -> List[List[str]]:
    # Convert every line into list of uppercase letters
    return [[char.upper() for char in line.strip()] for line in lines]