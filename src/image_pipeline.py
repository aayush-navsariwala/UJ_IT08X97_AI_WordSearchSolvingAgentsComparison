from typing import List, Optional


class ImageGridExtractor:
    def __init__(self):
        pass

    def load_image(self, image_path: str):
        raise NotImplementedError("Image loading not implemented yet.")

    def preprocess_image(self, image):
        raise NotImplementedError("Preprocessing not implemented yet.")

    def detect_grid_cells(self, processed_image):
        raise NotImplementedError("Grid detection not implemented yet.")

    def recognise_letters(self, cell_images) -> List[List[str]]:
        raise NotImplementedError("Letter recognition not implemented yet.")

    def extract_grid(self, image_path: str) -> Optional[List[List[str]]]:
        image = self.load_image(image_path)
        processed = self.preprocess_image(image)
        cells = self.detect_grid_cells(processed)
        grid = self.recognise_letters(cells)
        return grid