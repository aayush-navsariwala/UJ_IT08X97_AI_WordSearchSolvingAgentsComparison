import os
import shutil
from datetime import datetime
from typing import List, Optional

class ExperimentManager:
    def __init__(self, base_dir: str = "results/experiments"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.experiment_dir = os.path.join(base_dir, f"experiment_{timestamp}")

        self.graphs_dir = os.path.join(self.experiment_dir, "graphs")
        self.inputs_dir = os.path.join(self.experiment_dir, "inputs")

        os.makedirs(self.graphs_dir, exist_ok=True)
        os.makedirs(self.inputs_dir, exist_ok=True)

    def save_uploaded_image(self, image_path: Optional[str]):
        if not image_path:
            return None

        filename = os.path.basename(image_path)
        destination = os.path.join(self.inputs_dir, filename)
        shutil.copy2(image_path, destination)
        return destination

    def save_grid(self, grid_data: List[List[str]], filename: str):
        path = os.path.join(self.inputs_dir, filename)

        with open(path, "w", encoding="utf-8") as file:
            for row in grid_data:
                file.write("".join(row) + "\n")

        return path

    def save_words(self, words: List[str]):
        path = os.path.join(self.inputs_dir, "target_words.txt")

        with open(path, "w", encoding="utf-8") as file:
            for word in words:
                file.write(word + "\n")

        return path

    def save_summary(self, summary: str):
        path = os.path.join(self.experiment_dir, "experiment_summary.txt")

        with open(path, "w", encoding="utf-8") as file:
            file.write(summary)

        return path