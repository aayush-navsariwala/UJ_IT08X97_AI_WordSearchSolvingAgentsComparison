import os
import shutil
from datetime import datetime
from typing import List, Optional

class ExperimentManager:
    def __init__(self, base_dir: str = "results/experiments"):
        # Generate timestamp for experiment 
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create experiment directory
        self.experiment_dir = os.path.join(base_dir, f"experiment_{timestamp}")

        # Create folders for graphs and inputs
        self.graphs_dir = os.path.join(self.experiment_dir, "graphs")
        self.inputs_dir = os.path.join(self.experiment_dir, "inputs")

        # Create directories if they don't exist
        os.makedirs(self.graphs_dir, exist_ok=True)
        os.makedirs(self.inputs_dir, exist_ok=True)

    def save_uploaded_image(self, image_path: Optional[str]):
        # Return if no image provided
        if not image_path:
            return None

        # Extract image filename
        filename = os.path.basename(image_path)

        # Create destination path inside experiment
        destination = os.path.join(self.inputs_dir, filename)

        # Copy image into experiment
        shutil.copy2(image_path, destination)

        return destination

    def save_grid(self, grid_data: List[List[str]], filename: str):
        # Create full path for grid file
        path = os.path.join(self.inputs_dir, filename)

        # Save grid contents to text file
        with open(path, "w", encoding="utf-8") as file:
            for row in grid_data:
                file.write("".join(row) + "\n")

        return path

    def save_words(self, words: List[str]):
        # Create output path for target word list
        path = os.path.join(self.inputs_dir, "target_words.txt")

        # Save target word on separate line
        with open(path, "w", encoding="utf-8") as file:
            for word in words:
                file.write(word + "\n")

        return path

    def save_summary(self, summary: str):
        # Create output path for experiment summary
        path = os.path.join(self.experiment_dir, "experiment_summary.txt")

        # Save summary text to file
        with open(path, "w", encoding="utf-8") as file:
            file.write(summary)

        return path