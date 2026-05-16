import ast
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.visualiser import ResultVisualiser
from src.manual_input import load_grid_from_lines


class WordSearchAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Word Search Algorithm Comparison")
        self.root.geometry("1250x800")

        self.image_path = None
        self.latest_df = None
        self.current_grid_data = None
        self.grid_labels = []

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="AI Word Search Algorithm Comparison Agent",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        centre_frame = tk.Frame(main_frame)
        centre_frame.pack(side="left", fill="both", expand=True, padx=10)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        tk.Label(left_frame, text="Enter Word Search Grid", font=("Arial", 12, "bold")).pack(anchor="w")

        self.grid_text = tk.Text(left_frame, height=15, width=35)
        self.grid_text.pack(pady=5)

        self.grid_text.insert(
            "1.0",
            "CATDO\n"
            "XZOGG\n"
            "YDOGP\n"
            "BIRDQ\n"
            "FISHR"
        )

        tk.Label(left_frame, text="Enter Target Words", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        self.words_entry = tk.Entry(left_frame, width=40)
        self.words_entry.pack(pady=5)
        self.words_entry.insert(0, "CAT, DOG, BIRD, FISH, GOOD")

        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=15)

        tk.Button(
            button_frame,
            text="Run Benchmark",
            command=self.run_benchmark,
            bg="#1f4e79",
            fg="white",
            width=18
        ).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Upload Image",
            command=self.upload_image,
            width=18
        ).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
            width=18
        ).grid(row=1, column=0, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Save Current Input",
            command=self.save_current_input,
            width=18
        ).grid(row=1, column=1, padx=5, pady=5)

        self.status_label = tk.Label(left_frame, text="Ready", fg="green")
        self.status_label.pack(anchor="w", pady=5)

        tk.Label(centre_frame, text="Grid Path Visualisation", font=("Arial", 12, "bold")).pack(anchor="w")

        self.grid_display_frame = tk.Frame(centre_frame)
        self.grid_display_frame.pack(pady=10)

        self.path_label = tk.Label(
            centre_frame,
            text="Select a successful result to view its path.",
            wraplength=300,
            justify="left"
        )
        self.path_label.pack(anchor="w", pady=10)

        self.render_grid_from_input()

        tk.Label(right_frame, text="Benchmark Results", font=("Arial", 12, "bold")).pack(anchor="w")

        columns = (
            "algorithm",
            "word",
            "success",
            "time",
            "nodes",
            "states",
            "frontier",
            "path_len"
        )

        self.results_table = ttk.Treeview(right_frame, columns=columns, show="headings", height=25)

        headings = {
            "algorithm": "Algorithm",
            "word": "Word",
            "success": "Success",
            "time": "Time ms",
            "nodes": "Nodes",
            "states": "States",
            "frontier": "Max Frontier",
            "path_len": "Path Length"
        }

        widths = {
            "algorithm": 150,
            "word": 80,
            "success": 70,
            "time": 80,
            "nodes": 80,
            "states": 80,
            "frontier": 90,
            "path_len": 80
        }

        for col in columns:
            self.results_table.heading(col, text=headings[col])
            self.results_table.column(col, width=widths[col])

        self.results_table.pack(fill="both", expand=True, pady=5)
        self.results_table.bind("<<TreeviewSelect>>", self.on_result_selected)

        graph_button_frame = tk.Frame(right_frame)
        graph_button_frame.pack(pady=10)

        tk.Button(
            graph_button_frame,
            text="Open Results Folder",
            command=self.open_results_folder,
            width=22
        ).grid(row=0, column=0, padx=5)

    def get_grid_input(self):
        raw_grid = self.grid_text.get("1.0", tk.END).strip()

        if not raw_grid:
            raise ValueError("Grid input is empty.")

        lines = [line.strip().replace(" ", "") for line in raw_grid.splitlines() if line.strip()]

        if len(lines) == 0:
            raise ValueError("No valid grid rows found.")

        row_length = len(lines[0])

        for line in lines:
            if len(line) != row_length:
                raise ValueError("All grid rows must have the same length.")

            if not line.isalpha():
                raise ValueError("Grid must contain letters only.")

        return load_grid_from_lines(lines)

    def get_words_input(self):
        raw_words = self.words_entry.get().strip()

        if not raw_words:
            raise ValueError("Word list is empty.")

        words = [word.strip().upper() for word in raw_words.split(",") if word.strip()]

        if len(words) == 0:
            raise ValueError("No valid target words found.")

        for word in words:
            if not word.isalpha():
                raise ValueError("Target words must contain letters only.")

        return words

    def run_benchmark(self):
        try:
            self.status_label.config(text="Running benchmark...", fg="orange")
            self.root.update_idletasks()

            self.current_grid_data = self.get_grid_input()
            words = self.get_words_input()

            self.render_grid(self.current_grid_data)

            grid = WordSearchGrid(self.current_grid_data)

            benchmark = BenchmarkRunner()
            df = benchmark.run(grid, words)
            self.latest_df = df

            os.makedirs("results", exist_ok=True)

            export_df = df.copy()
            export_df["path"] = export_df["path"].apply(lambda p: str(p))
            export_df.to_csv("results/gui_benchmark_results.csv", index=False)

            visualiser = ResultVisualiser()
            visualiser.plot_metric_by_algorithm(df, "execution_time_ms", "gui_time_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "nodes_expanded", "gui_nodes_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "states_generated", "gui_states_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "max_frontier_size", "gui_frontier_comparison.png")

            self.populate_table(df)

            self.status_label.config(
                text="Benchmark complete. Select a result to view its path.",
                fg="green"
            )

        except Exception as e:
            self.status_label.config(text="Error", fg="red")
            messagebox.showerror("Benchmark Error", str(e))

    def populate_table(self, df: pd.DataFrame):
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        for index, row in df.iterrows():
            self.results_table.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    row["algorithm"],
                    row["word"],
                    row["success"],
                    round(row["execution_time_ms"], 3),
                    row["nodes_expanded"],
                    row["states_generated"],
                    row["max_frontier_size"],
                    row["path_length"]
                )
            )

    def on_result_selected(self, event):
        selected = self.results_table.selection()

        if not selected or self.latest_df is None:
            return

        index = int(selected[0])
        row = self.latest_df.iloc[index]

        path = row["path"]

        if isinstance(path, str):
            try:
                path = ast.literal_eval(path)
            except Exception:
                path = []

        if not row["success"] or not path:
            self.render_grid(self.current_grid_data)
            self.path_label.config(
                text=f"{row['algorithm']} did not find {row['word']}."
            )
            return

        self.highlight_path(path)

        self.path_label.config(
            text=(
                f"Algorithm: {row['algorithm']}\n"
                f"Word: {row['word']}\n"
                f"Path: {path}"
            )
        )

    def render_grid_from_input(self):
        try:
            grid_data = self.get_grid_input()
            self.current_grid_data = grid_data
            self.render_grid(grid_data)
        except Exception:
            pass

    def render_grid(self, grid_data):
        for widget in self.grid_display_frame.winfo_children():
            widget.destroy()

        self.grid_labels = []

        for r, row in enumerate(grid_data):
            label_row = []
            for c, letter in enumerate(row):
                label = tk.Label(
                    self.grid_display_frame,
                    text=letter,
                    width=3,
                    height=1,
                    borderwidth=1,
                    relief="solid",
                    font=("Arial", 14, "bold"),
                    bg="white"
                )
                label.grid(row=r, column=c, padx=1, pady=1)
                label_row.append(label)
            self.grid_labels.append(label_row)

    def highlight_path(self, path):
        if self.current_grid_data is None:
            return

        self.render_grid(self.current_grid_data)

        visit_counts = {}

        for step, (row, col) in enumerate(path, start=1):
            if row < 0 or col < 0:
                continue

            if row >= len(self.grid_labels) or col >= len(self.grid_labels[row]):
                continue

            visit_counts[(row, col)] = visit_counts.get((row, col), 0) + 1

            label = self.grid_labels[row][col]
            label.config(bg="#ffe699", fg="black")

            if visit_counts[(row, col)] > 1:
                label.config(bg="#f4b183")

            label.config(text=f"{self.current_grid_data[row][col]}\n{step}")

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select Word Search Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
                ("All Files", "*.*")
            ]
        )

        if self.image_path:
            messagebox.showinfo(
                "Image Selected",
                "Image upload has been added, but OCR extraction is not connected yet.\n\n"
                f"Selected file:\n{self.image_path}"
            )

            self.status_label.config(
                text="Image selected. OCR extraction not implemented yet.",
                fg="blue"
            )

    def clear_results(self):
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        if self.current_grid_data:
            self.render_grid(self.current_grid_data)

        self.path_label.config(text="Select a successful result to view its path.")
        self.status_label.config(text="Results cleared.", fg="green")

    def save_current_input(self):
        os.makedirs("results", exist_ok=True)

        grid_content = self.grid_text.get("1.0", tk.END).strip()
        words_content = self.words_entry.get().strip()

        with open("results/current_input.txt", "w", encoding="utf-8") as file:
            file.write("GRID:\n")
            file.write(grid_content)
            file.write("\n\nWORDS:\n")
            file.write(words_content)

        messagebox.showinfo("Saved", "Current grid and word list saved to results/current_input.txt")

    def open_results_folder(self):
        results_path = os.path.abspath("results")

        if not os.path.exists(results_path):
            os.makedirs(results_path)

        try:
            os.startfile(results_path)
        except AttributeError:
            messagebox.showinfo("Results Folder", results_path)


def main():
    root = tk.Tk()
    WordSearchAIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()