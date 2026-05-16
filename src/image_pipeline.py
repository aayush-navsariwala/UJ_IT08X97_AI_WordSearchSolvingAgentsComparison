import cv2
import pytesseract
from typing import List

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ImageGridExtractor:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols

    def load_image(self, image_path: str):
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError("Could not load image.")

        return image

    def preprocess_image(self, image):
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        grey = cv2.GaussianBlur(grey, (3, 3), 0)

        threshold = cv2.adaptiveThreshold(
            grey,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )

        return threshold

    def split_into_cells(self, image):
        height, width = image.shape[:2]

        cell_height = height // self.rows
        cell_width = width // self.cols

        cells = []

        for r in range(self.rows):
            row_cells = []

            for c in range(self.cols):
                y1 = r * cell_height
                y2 = (r + 1) * cell_height
                x1 = c * cell_width
                x2 = (c + 1) * cell_width

                cell = image[y1:y2, x1:x2]

                margin_y = max(1, cell_height // 10)
                margin_x = max(1, cell_width // 10)

                cell = cell[
                    margin_y:cell.shape[0] - margin_y,
                    margin_x:cell.shape[1] - margin_x
                ]

                row_cells.append(cell)

            cells.append(row_cells)

        return cells

    def recognise_letter(self, cell_image) -> str:
        resized = cv2.resize(cell_image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        config = (
            "--psm 10 "
            "--oem 3 "
            "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

        text = pytesseract.image_to_string(resized, config=config)
        text = text.strip().upper()

        if len(text) == 0:
            return "?"

        for char in text:
            if char.isalpha():
                return char

        return "?"

    def recognise_grid(self, cells) -> List[List[str]]:
        grid = []

        for row_cells in cells:
            row = []

            for cell in row_cells:
                letter = self.recognise_letter(cell)
                row.append(letter)

            grid.append(row)

        return grid

    def extract_grid(self, image_path: str) -> List[List[str]]:
        image = self.load_image(image_path)
        processed = self.preprocess_image(image)
        cells = self.split_into_cells(processed)
        grid = self.recognise_grid(cells)

        return grid