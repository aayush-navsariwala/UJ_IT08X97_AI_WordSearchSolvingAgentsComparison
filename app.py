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
        self.root.geometry("1100x750")

        self.image_path = None

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

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        tk.Label(left_frame, text="Enter Word Search Grid", font=("Arial", 12, "bold")).pack(anchor="w")

        self.grid_text = tk.Text(left_frame, height=15, width=45)
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

        self.words_entry = tk.Entry(left_frame, width=50)
        self.words_entry.pack(pady=5)
        self.words_entry.insert(0, "CAT, DOG, BIRD, FISH, GOOD")

        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=15)

        run_button = tk.Button(
            button_frame,
            text="Run Benchmark",
            command=self.run_benchmark,
            bg="#1f4e79",
            fg="white",
            width=18
        )
        run_button.grid(row=0, column=0, padx=5)

        upload_button = tk.Button(
            button_frame,
            text="Upload Image",
            command=self.upload_image,
            width=18
        )
        upload_button.grid(row=0, column=1, padx=5)

        clear_button = tk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
            width=18
        )
        clear_button.grid(row=0, column=2, padx=5)

        self.status_label = tk.Label(left_frame, text="Ready", fg="green")
        self.status_label.pack(anchor="w", pady=5)

        tk.Label(right_frame, text="Benchmark Results", font=("Arial", 12, "bold")).pack(anchor="w")

        columns = (
            "algorithm",
            "word",
            "success",
            "time",
            "nodes",
            "states",
            "frontier",
            "path"
        )

        self.results_table = ttk.Treeview(right_frame, columns=columns, show="headings", height=22)

        self.results_table.heading("algorithm", text="Algorithm")
        self.results_table.heading("word", text="Word")
        self.results_table.heading("success", text="Success")
        self.results_table.heading("time", text="Time ms")
        self.results_table.heading("nodes", text="Nodes")
        self.results_table.heading("states", text="States")
        self.results_table.heading("frontier", text="Max Frontier")
        self.results_table.heading("path", text="Path Length")

        self.results_table.column("algorithm", width=150)
        self.results_table.column("word", width=80)
        self.results_table.column("success", width=70)
        self.results_table.column("time", width=80)
        self.results_table.column("nodes", width=80)
        self.results_table.column("states", width=80)
        self.results_table.column("frontier", width=90)
        self.results_table.column("path", width=80)

        self.results_table.pack(fill="both", expand=True, pady=5)

        graph_button_frame = tk.Frame(right_frame)
        graph_button_frame.pack(pady=10)

        tk.Button(
            graph_button_frame,
            text="Open Results Folder",
            command=self.open_results_folder,
            width=22
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            graph_button_frame,
            text="Save Current Input",
            command=self.save_current_input,
            width=22
        ).grid(row=0, column=1, padx=5)

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

            grid_data = self.get_grid_input()
            words = self.get_words_input()

            grid = WordSearchGrid(grid_data)

            benchmark = BenchmarkRunner()
            df = benchmark.run(grid, words)

            os.makedirs("results", exist_ok=True)
            df.to_csv("results/gui_benchmark_results.csv", index=False)

            visualiser = ResultVisualiser()
            visualiser.plot_metric_by_algorithm(df, "execution_time_ms", "gui_time_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "nodes_expanded", "gui_nodes_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "states_generated", "gui_states_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "max_frontier_size", "gui_frontier_comparison.png")

            self.populate_table(df)

            self.status_label.config(
                text="Benchmark complete. Results saved in /results.",
                fg="green"
            )

        except Exception as e:
            self.status_label.config(text="Error", fg="red")
            messagebox.showerror("Benchmark Error", str(e))

    def populate_table(self, df: pd.DataFrame):
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        for _, row in df.iterrows():
            self.results_table.insert(
                "",
                tk.END,
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
    app = WordSearchAIApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()