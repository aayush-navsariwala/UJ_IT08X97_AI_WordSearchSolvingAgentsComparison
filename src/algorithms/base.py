from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from src.grid import WordSearchGrid
from src.metrics import SearchMetrics

Position = Tuple[int, int]

class BaseSearchAlgorithm(ABC):
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def search(self, grid: WordSearchGrid, word: str) -> tuple[Optional[List[Position]], SearchMetrics]:
        pass