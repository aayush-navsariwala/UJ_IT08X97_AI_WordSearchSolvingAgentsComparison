import ast
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd

from src.grid import WordSearchGrid
from src.benchmark import BenchmarkRunner
from src.visualiser import ResultVisualiser
from src.manual_input import load_grid_from_lines
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from src.image_pipeline import ImageGridExtractor
from src.experiment_manager import ExperimentManager
from src.report_generator import ReportGenerator

class WordSearchAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Word Search Algorithm Comparison")
        self.root.geometry("1250x800")

        self.image_path = None
        self.latest_df = None
        self.current_grid_data = None
        self.grid_labels = []
        self.current_experiment_dir = None

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
        
        tk.Label(left_frame, text="Image Grid Size", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        size_frame = tk.Frame(left_frame)
        size_frame.pack(anchor="w", pady=5)

        tk.Label(size_frame, text="Rows:").grid(row=0, column=0, padx=3)

        self.rows_entry = tk.Entry(size_frame, width=6)
        self.rows_entry.grid(row=0, column=1, padx=3)
        self.rows_entry.insert(0, "5")

        tk.Label(size_frame, text="Columns:").grid(row=0, column=2, padx=3)

        self.cols_entry = tk.Entry(size_frame, width=6)
        self.cols_entry.grid(row=0, column=3, padx=3)
        self.cols_entry.insert(0, "5")

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

        results_pane = tk.PanedWindow(
            right_frame,
            orient=tk.VERTICAL,
            sashrelief=tk.RAISED,
            sashwidth=6
        )

        results_pane.pack(fill="both", expand=True)

        table_container = tk.Frame(results_pane)
        graph_container = tk.Frame(results_pane)

        results_pane.add(table_container, minsize=250)
        results_pane.add(graph_container, minsize=350)

        tk.Label(
            table_container,
            text="Benchmark Results",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

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

        self.results_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=10
        )

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

        table_scroll_y = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.results_table.yview
        )

        self.results_table.configure(yscrollcommand=table_scroll_y.set)

        self.results_table.pack(side="left", fill="both", expand=True, pady=5)
        table_scroll_y.pack(side="right", fill="y")
        
        self.results_table.bind("<<TreeviewSelect>>", self.on_result_selected)
        
        tk.Label(
            graph_container,
            text="Graph Preview",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(10, 0))

        self.graph_metric = tk.StringVar(value="execution_time_ms")

        graph_options = ttk.Combobox(
            graph_container,
            textvariable=self.graph_metric,
            values=[
                "execution_time_ms",
                "nodes_expanded",
                "states_generated",
                "max_frontier_size"
            ],
            state="readonly",
            width=30
        )
        graph_options.pack(anchor="w", pady=5)
        graph_options.bind("<<ComboboxSelected>>", self.update_graph_preview)

        self.graph_frame = tk.Frame(graph_container)
        self.graph_frame.pack(fill="both", expand=True, pady=5)

        self.graph_canvas = None

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
            text="Generate Report",
            command=self.generate_report,
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

            experiment = ExperimentManager()

            self.current_grid_data = self.get_grid_input()
            words = self.get_words_input()

            experiment.save_uploaded_image(self.image_path)
            experiment.save_grid(self.current_grid_data, "corrected_grid.txt")
            experiment.save_words(words)

            self.render_grid(self.current_grid_data)

            grid = WordSearchGrid(self.current_grid_data)

            benchmark = BenchmarkRunner()
            df = benchmark.run(grid, words)
            self.latest_df = df

            export_df = df.copy()
            export_df["path"] = export_df["path"].apply(lambda p: str(p))

            csv_path = os.path.join(experiment.experiment_dir, "benchmark_results.csv")
            export_df.to_csv(csv_path, index=False)

            visualiser = ResultVisualiser(output_dir=experiment.graphs_dir)
            visualiser.plot_metric_by_algorithm(df, "execution_time_ms", "time_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "nodes_expanded", "nodes_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "states_generated", "states_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "max_frontier_size", "frontier_comparison.png")

            summary = (
                "AI Word Search Algorithm Comparison Experiment\n\n"
                f"Experiment folder: {experiment.experiment_dir}\n"
                f"Rows: {len(self.current_grid_data)}\n"
                f"Columns: {len(self.current_grid_data[0])}\n"
                f"Target words: {', '.join(words)}\n\n"
                "Algorithms compared:\n"
                "- DFS\n"
                "- BFS\n"
                "- IDDFS\n"
                "- Greedy Best-First Search\n"
                "- A*\n"
                "- Beam Search\n\n"
                "Metrics recorded:\n"
                "- Execution time\n"
                "- Nodes expanded\n"
                "- States generated\n"
                "- Maximum frontier size\n"
                "- Success status\n"
                "- Path length\n"
            )

            experiment.save_summary(summary)

            self.populate_table(df)
            self.update_graph_preview()

            self.current_experiment_dir = experiment.experiment_dir

            self.status_label.config(
                text=f"Benchmark complete. Saved to {experiment.experiment_dir}",
                fg="green"
            )

            messagebox.showinfo(
                "Experiment Saved",
                f"Experiment saved successfully:\n\n{experiment.experiment_dir}"
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

        if not self.image_path:
            return

        try:
            rows = int(self.rows_entry.get().strip())
            cols = int(self.cols_entry.get().strip())

            if rows <= 0 or cols <= 0:
                raise ValueError("Rows and columns must be positive numbers.")

            self.status_label.config(text="Extracting grid from image...", fg="orange")
            self.root.update_idletasks()

            extractor = ImageGridExtractor(rows=rows, cols=cols)
            extracted_grid = extractor.extract_grid(self.image_path)

            grid_text = "\n".join("".join(row) for row in extracted_grid)

            self.grid_text.delete("1.0", tk.END)
            self.grid_text.insert("1.0", grid_text)

            self.current_grid_data = extracted_grid
            self.render_grid(extracted_grid)

            self.status_label.config(
                text="Image extracted. Please check and correct any '?' characters.",
                fg="blue"
            )

            messagebox.showinfo(
                "Grid Extracted",
                "The image has been converted into a grid.\n\n"
                "Please review the grid before running the benchmark."
            )

        except Exception as e:
            self.status_label.config(text="Image extraction failed.", fg="red")
            messagebox.showerror("Image Extraction Error", str(e))

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
        if hasattr(self, "current_experiment_dir") and self.current_experiment_dir:
            results_path = os.path.abspath(self.current_experiment_dir)
        else:
            results_path = os.path.abspath("results")

        if not os.path.exists(results_path):
            os.makedirs(results_path)

        try:
            os.startfile(results_path)
        except AttributeError:
            messagebox.showinfo("Results Folder", results_path)
            
    def update_graph_preview(self, event=None):
        if self.latest_df is None:
            return

        metric = self.graph_metric.get()

        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        grouped = (
            self.latest_df
            .groupby("algorithm")[metric]
            .mean()
            .sort_values()
        )

        fig = Figure(figsize=(8.5, 5.2), dpi=100)
        ax = fig.add_subplot(111)

        grouped.plot(kind="bar", ax=ax)

        ax.set_title(f"Average {metric.replace('_', ' ').title()}")
        ax.set_xlabel("Algorithm")
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.tick_params(axis="x", rotation=35)

        fig.tight_layout()

        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def generate_report(self):
        if self.latest_df is None:
            messagebox.showwarning("No Results", "Run a benchmark before generating a report.")
            return

        if not self.current_experiment_dir:
            messagebox.showwarning("No Experiment", "No experiment folder found.")
            return

        try:
            words = self.get_words_input()

            report_generator = ReportGenerator(self.current_experiment_dir)
            report_path = report_generator.generate_txt_report(
                self.latest_df,
                self.current_grid_data,
                words
            )

            messagebox.showinfo(
                "Report Generated",
                f"Report generated successfully:\n\n{report_path}"
            )

            self.status_label.config(
                text=f"Report generated: {report_path}",
                fg="green"
            )

        except Exception as e:
            messagebox.showerror("Report Error", str(e))


def main():
    root = tk.Tk()
    WordSearchAIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()