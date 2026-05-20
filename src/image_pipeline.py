import cv2
import pytesseract
from typing import List, Tuple

# Set local tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ImageGridExtractor:
    # Store default number of grid rows, columns and auto detect them
    def __init__(self, rows: int = 5, cols: int = 5, auto_detect: bool = True):
        self.rows = rows
        self.cols = cols
        self.auto_detect = auto_detect

    def load_image(self, image_path: str):
        # Load image from file path
        image = cv2.imread(image_path)

        # Raise error if image cannot be loaded
        if image is None:
            raise ValueError("Could not load image.")
        return image

    def preprocess_image(self, image):
        # Convert image to greyscale
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Reduce noise before thresholding
        grey = cv2.GaussianBlur(grey, (3, 3), 0)

        # Convert image into high contrast binary image
        threshold = cv2.adaptiveThreshold(
            grey,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )
        return threshold
    
    def detect_grid_size(self, processed_image) -> Tuple[int, int]:
        height, width = processed_image.shape[:2]

        horizontal_projection = processed_image.sum(axis=1)
        vertical_projection = processed_image.sum(axis=0)

        def count_gaps(projection, min_gap_size=5):
            threshold = projection.max() * 0.15
            empty_regions = []
            in_gap = False
            start = 0

            for i, value in enumerate(projection):
                if value < threshold and not in_gap:
                    in_gap = True
                    start = i
                elif value >= threshold and in_gap:
                    in_gap = False
                    if i - start >= min_gap_size:
                        empty_regions.append((start, i))

            if in_gap:
                empty_regions.append((start, len(projection)))

            return len(empty_regions)

        row_gaps = count_gaps(horizontal_projection)
        col_gaps = count_gaps(vertical_projection)

        estimated_rows = max(1, row_gaps + 1)
        estimated_cols = max(1, col_gaps + 1)

        if 2 <= estimated_rows <= 30 and 2 <= estimated_cols <= 30:
            return estimated_rows, estimated_cols

        return self.rows, self.cols

    def merge_close_positions(self, positions, tolerance: int = 10):
        if not positions:
            return []

        merged = [positions[0]]

        for pos in positions[1:]:
            if abs(pos - merged[-1]) > tolerance:
                merged.append(pos)

        return merged

    def split_into_cells(self, image):
        # Get image dimensions
        height, width = image.shape[:2]

        # Calculate size of every cell
        cell_height = height // self.rows
        cell_width = width // self.cols

        # Store extracted cell images
        cells = []

        # Split image into row and column cells
        for r in range(self.rows):
            row_cells = []

            for c in range(self.cols):
                # Calculate cell boundaries
                y1 = r * cell_height
                y2 = (r + 1) * cell_height
                x1 = c * cell_width
                x2 = (c + 1) * cell_width

                # Crop current cell from image
                cell = image[y1:y2, x1:x2]

                # Add small margin to reduce grid line interference
                margin_y = max(1, cell_height // 10)
                margin_x = max(1, cell_width // 10)

                # Crop out margin around cell
                cell = cell[
                    margin_y:cell.shape[0] - margin_y,
                    margin_x:cell.shape[1] - margin_x
                ]

                # Add processed cell to current row
                row_cells.append(cell)

            # Add the completed row of cells
            cells.append(row_cells)
        return cells

    def recognise_letter(self, cell_image) -> str:
        # Enlarge cell to improve OCR accuracy
        resized = cv2.resize(cell_image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # Set OCR to recognise single uppercase letter 
        config = (
            "--psm 10 "
            "--oem 3 "
            "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

        # Run OCR on cell image
        text = pytesseract.image_to_string(resized, config=config)

        # Clean recognised text
        text = text.strip().upper()

        # Return placeholder if no letter recognised
        if len(text) == 0:
            return "?"

        # Return first alphabetic character
        for char in text:
            if char.isalpha():
                return char

        # Return placeholder if OCR output is invalid
        return "?"

    def recognise_grid(self, cells) -> List[List[str]]:
        # Store recognised letter grid
        grid = []

        # Process each row of cell images
        for row_cells in cells:
            row = []

            # Recognise each cell as single letter
            for cell in row_cells:
                row.append(self.recognise_letter(cell))

            # Add recognised row to grid
            grid.append(row)

        return grid

    def extract_grid(self, image_path: str):
        image = self.load_image(image_path)
        processed = self.preprocess_image(image)

        if self.auto_detect:
            self.rows, self.cols = self.detect_grid_size(processed)

        cells = self.split_into_cells(processed)
        grid = self.recognise_grid(cells)

        return grid, self.rows, self.cols