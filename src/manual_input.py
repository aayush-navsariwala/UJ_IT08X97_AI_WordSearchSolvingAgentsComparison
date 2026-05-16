from typing import List

def load_grid_from_lines(lines: List[str]) -> List[List[str]]:
    return [[char.upper() for char in line.strip()] for line in lines]