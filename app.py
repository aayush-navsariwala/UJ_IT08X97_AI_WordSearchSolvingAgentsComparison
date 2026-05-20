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
        # Store main Tkinter window
        self.root = root

        # Configure main application window
        self.root.title("AI Word Search Algorithm Comparison")
        self.root.geometry("1250x800")

        # Store uploaded image path
        self.image_path = None

        # Store latest benchmark dataframe
        self.latest_df = None

        # Store current grid data
        self.current_grid_data = None

        # Store all visual grid labels
        self.grid_labels = []

        # Store current experiment folder path
        self.current_experiment_dir = None

        # Build GUI components
        self.create_widgets()

    def create_widgets(self):
        # Create application title
        title = tk.Label(
            self.root,
            text="AI Word Search Algorithm Comparison Agent",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        # Create main container frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Create left input panel
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        # Create centre visualisation panel
        centre_frame = tk.Frame(main_frame)
        centre_frame.pack(side="left", fill="both", expand=True, padx=10)

        # Create right results panel
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        # Create grid input label
        tk.Label(left_frame, text="Enter Word Search Grid", font=("Arial", 12, "bold")).pack(anchor="w")

        # Create grid input text area
        self.grid_text = tk.Text(left_frame, height=15, width=35)
        self.grid_text.pack(pady=5)

        # Insert default example grid data
        self.grid_text.insert(
            "1.0",
            "CATDO\n"
            "XZOGG\n"
            "YDOGP\n"
            "BIRDQ\n"
            "FISHR"
        )

        # Create target word label
        tk.Label(left_frame, text="Enter Target Words", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        # Create target word entry field
        self.words_entry = tk.Entry(left_frame, width=40)
        self.words_entry.pack(pady=5)

        # Insert default target words
        self.words_entry.insert(0, "CAT, DOG, BIRD, FISH, GOOD")

        # Create image grid size label
        tk.Label(left_frame, text="Image Grid Size", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))

        # Create image grid size container
        size_frame = tk.Frame(left_frame)
        size_frame.pack(anchor="w", pady=5)

        # Create row input label
        tk.Label(size_frame, text="Rows:").grid(row=0, column=0, padx=3)

        # Create row input field
        self.rows_entry = tk.Entry(size_frame, width=6)
        self.rows_entry.grid(row=0, column=1, padx=3)

        # Insert default row value
        self.rows_entry.insert(0, "5")

        # Create column input label
        tk.Label(size_frame, text="Columns:").grid(row=0, column=2, padx=3)

        # Create column input field
        self.cols_entry = tk.Entry(size_frame, width=6)
        self.cols_entry.grid(row=0, column=3, padx=3)

        # Insert default column value
        self.cols_entry.insert(0, "5")

        # Create button container
        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=15)

        # Create benchmark execution button
        tk.Button(
            button_frame,
            text="Run Benchmark",
            command=self.run_benchmark,
            bg="#1f4e79",
            fg="white",
            width=18
        ).grid(row=0, column=0, padx=5, pady=5)

        # Create image upload button
        tk.Button(
            button_frame,
            text="Upload Image",
            command=self.upload_image,
            width=18
        ).grid(row=0, column=1, padx=5, pady=5)

        # Create clear results button
        tk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
            width=18
        ).grid(row=1, column=0, padx=5, pady=5)

        # Create save input button
        tk.Button(
            button_frame,
            text="Save Current Input",
            command=self.save_current_input,
            width=18
        ).grid(row=1, column=1, padx=5, pady=5)

        # Create application status label
        self.status_label = tk.Label(left_frame, text="Ready", fg="green")
        self.status_label.pack(anchor="w", pady=5)

        # Create visualisation section title
        tk.Label(centre_frame, text="Grid Path Visualisation", font=("Arial", 12, "bold")).pack(anchor="w")

        # Create visual grid display frame
        self.grid_display_frame = tk.Frame(centre_frame)
        self.grid_display_frame.pack(pady=10)

        # Create selected path information label
        self.path_label = tk.Label(
            centre_frame,
            text="Select a successful result to view its path.",
            wraplength=300,
            justify="left"
        )
        self.path_label.pack(anchor="w", pady=10)

        # Render initial grid
        self.render_grid_from_input()

        # Create resizable results panel
        results_pane = tk.PanedWindow(
            right_frame,
            orient=tk.VERTICAL,
            sashrelief=tk.RAISED,
            sashwidth=6
        )

        results_pane.pack(fill="both", expand=True)

        # Create table and graph containers
        table_container = tk.Frame(results_pane)
        graph_container = tk.Frame(results_pane)

        # Add containers to resizable panel
        results_pane.add(table_container, minsize=250)
        results_pane.add(graph_container, minsize=350)

        # Create results section title
        tk.Label(
            table_container,
            text="Benchmark Results",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        # Define table columns
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

        # Create results table
        self.results_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=10
        )

        # Define column headings
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

        # Define column widths
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

        # Configure table headings and widths
        for col in columns:
            self.results_table.heading(col, text=headings[col])
            self.results_table.column(col, width=widths[col])

        # Create vertical scrollbar for results table
        table_scroll_y = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.results_table.yview
        )

        # Attach scrollbar to table
        self.results_table.configure(yscrollcommand=table_scroll_y.set)

        # Display table and scrollbar
        self.results_table.pack(side="left", fill="both", expand=True, pady=5)
        table_scroll_y.pack(side="right", fill="y")

        # Bind row selection events
        self.results_table.bind("<<TreeviewSelect>>", self.on_result_selected)

        # Create graph preview section title
        tk.Label(
            graph_container,
            text="Graph Preview",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(10, 0))

        # Store currently selected graph metric
        self.graph_metric = tk.StringVar(value="execution_time_ms")

        # Create graph metric selection menu
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

        # Update graph when metric changes
        graph_options.bind("<<ComboboxSelected>>", self.update_graph_preview)

        # Create graph display frame
        self.graph_frame = tk.Frame(graph_container)
        self.graph_frame.pack(fill="both", expand=True, pady=5)

        # Store graph canvas object
        self.graph_canvas = None

        # Create graph button container
        graph_button_frame = tk.Frame(right_frame)
        graph_button_frame.pack(pady=10)

        # Create open results folder button
        tk.Button(
            graph_button_frame,
            text="Open Results Folder",
            command=self.open_results_folder,
            width=22
        ).grid(row=0, column=0, padx=5)

        # Create report generation button
        tk.Button(
            graph_button_frame,
            text="Generate Report",
            command=self.generate_report,
            width=22
        ).grid(row=0, column=1, padx=5)

    def get_grid_input(self):
        # Retrieve raw grid input from text area
        raw_grid = self.grid_text.get("1.0", tk.END).strip()

        # Stop if grid input is empty
        if not raw_grid:
            raise ValueError("Grid input is empty.")

        # Remove spaces and blank lines from input
        lines = [line.strip().replace(" ", "") for line in raw_grid.splitlines() if line.strip()]

        # Stop if no valid grid rows found
        if len(lines) == 0:
            raise ValueError("No valid grid rows found.")

        # Store expected row length
        row_length = len(lines[0])

        # Validate each row in grid
        for line in lines:
            # Ensure all rows have same length
            if len(line) != row_length:
                raise ValueError("All grid rows must have the same length.")

            # Ensure grid contains letters only
            if not line.isalpha():
                raise ValueError("Grid must contain letters only.")

        # Convert text input into grid data
        return load_grid_from_lines(lines)

    def get_words_input(self):
        # Retrieve raw target word input
        raw_words = self.words_entry.get().strip()

        # Stop if word list is empty
        if not raw_words:
            raise ValueError("Word list is empty.")

        # Split and clean target words
        words = [word.strip().upper() for word in raw_words.split(",") if word.strip()]

        # Stop if no valid words found
        if len(words) == 0:
            raise ValueError("No valid target words found.")

        # Validate every target word
        for word in words:
            # Ensure words contain letters only
            if not word.isalpha():
                raise ValueError("Target words must contain letters only.")

        return words

    def run_benchmark(self):
        try:
            # Update application status
            self.status_label.config(text="Running benchmark...", fg="orange")
            self.root.update_idletasks()

            # Create new experiment manager
            experiment = ExperimentManager()

            # Retrieve current grid and target words
            self.current_grid_data = self.get_grid_input()
            words = self.get_words_input()

            # Save experiment inputs
            experiment.save_uploaded_image(self.image_path)
            experiment.save_grid(self.current_grid_data, "corrected_grid.txt")
            experiment.save_words(words)

            # Render current grid visually
            self.render_grid(self.current_grid_data)

            # Create grid object
            grid = WordSearchGrid(self.current_grid_data)

            # Run benchmark comparison
            benchmark = BenchmarkRunner()
            df = benchmark.run(grid, words)

            # Store latest benchmark results
            self.latest_df = df

            # Create copy for exporting
            export_df = df.copy()

            # Convert paths to string format for CSV export
            export_df["path"] = export_df["path"].apply(lambda p: str(p))

            # Save benchmark results to CSV
            csv_path = os.path.join(experiment.experiment_dir, "benchmark_results.csv")
            export_df.to_csv(csv_path, index=False)

            # Generate benchmark graphs
            visualiser = ResultVisualiser(output_dir=experiment.graphs_dir)
            visualiser.plot_metric_by_algorithm(df, "execution_time_ms", "time_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "nodes_expanded", "nodes_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "states_generated", "states_comparison.png")
            visualiser.plot_metric_by_algorithm(df, "max_frontier_size", "frontier_comparison.png")

            # Create experiment summary text
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

            # Save experiment summary
            experiment.save_summary(summary)

            # Populate results table
            self.populate_table(df)

            # Update graph preview
            self.update_graph_preview()

            # Store current experiment directory
            self.current_experiment_dir = experiment.experiment_dir

            # Update application status
            self.status_label.config(
                text=f"Benchmark complete. Saved to {experiment.experiment_dir}",
                fg="green"
            )

            # Display success message
            messagebox.showinfo(
                "Experiment Saved",
                f"Experiment saved successfully:\n\n{experiment.experiment_dir}"
            )

        except Exception as e:
            # Display benchmark error information
            self.status_label.config(text="Error", fg="red")
            messagebox.showerror("Benchmark Error", str(e))

    def populate_table(self, df: pd.DataFrame):
        # Clear existing table rows
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        # Insert benchmark results into table
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
        # Retrieve selected table row
        selected = self.results_table.selection()

        # Stop if no result is selected
        if not selected or self.latest_df is None:
            return

        # Get selected dataframe
        index = int(selected[0])
        row = self.latest_df.iloc[index]

        # Retrieve stored path
        path = row["path"]

        # Convert string path data back into list
        if isinstance(path, str):
            try:
                path = ast.literal_eval(path)
            except Exception:
                path = []

        # Reset grid if no successful path exists
        if not row["success"] or not path:
            self.render_grid(self.current_grid_data)

            self.path_label.config(
                text=f"{row['algorithm']} did not find {row['word']}."
            )

            return

        # Highlight discovered path visually
        self.highlight_path(path)

        # Display path information
        self.path_label.config(
            text=(
                f"Algorithm: {row['algorithm']}\n"
                f"Word: {row['word']}\n"
                f"Path: {path}"
            )
        )

    def render_grid_from_input(self):
        try:
            # Retrieve current grid input
            grid_data = self.get_grid_input()

            # Store current grid data
            self.current_grid_data = grid_data

            # Render grid visually
            self.render_grid(grid_data)

        except Exception:
            # Ignore rendering errors during live updates
            pass

    def render_grid(self, grid_data):
        # Remove any existing grid labels
        for widget in self.grid_display_frame.winfo_children():
            widget.destroy()

        # Reset stored grid labels
        self.grid_labels = []

        # Create visual labels for each grid cell
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

                # Position label in grid
                label.grid(row=r, column=c, padx=1, pady=1)

                # Store label reference
                label_row.append(label)

            # Store completed label row
            self.grid_labels.append(label_row)

    def highlight_path(self, path):
        # Stop if no grid is currently loaded
        if self.current_grid_data is None:
            return

        # Reset grid before highlighting
        self.render_grid(self.current_grid_data)

        # Track how many times each cell is visited
        visit_counts = {}

        # Highlight each step in discovered path
        for step, (row, col) in enumerate(path, start=1):
            # Ignore invalid negative coordinates
            if row < 0 or col < 0:
                continue

            # Ignore coordinates outside displayed grid
            if row >= len(self.grid_labels) or col >= len(self.grid_labels[row]):
                continue

            # Count visits for reused cells
            visit_counts[(row, col)] = visit_counts.get((row, col), 0) + 1

            # Retrieve matching grid label
            label = self.grid_labels[row][col]

            # Highlight current cell
            label.config(bg="#ffe699", fg="black")

            # Use different colour for reused cells
            if visit_counts[(row, col)] > 1:
                label.config(bg="#f4b183")

            # Display letter and step number
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
            default_rows = int(self.rows_entry.get().strip() or 5)
            default_cols = int(self.cols_entry.get().strip() or 5)

            self.status_label.config(text="Detecting grid size and extracting letters...", fg="orange")
            self.root.update_idletasks()

            extractor = ImageGridExtractor(
                rows=default_rows,
                cols=default_cols,
                auto_detect=True
            )

            extracted_grid, detected_rows, detected_cols = extractor.extract_grid(self.image_path)

            self.rows_entry.delete(0, tk.END)
            self.rows_entry.insert(0, str(detected_rows))

            self.cols_entry.delete(0, tk.END)
            self.cols_entry.insert(0, str(detected_cols))

            grid_text = "\n".join("".join(row) for row in extracted_grid)

            self.grid_text.delete("1.0", tk.END)
            self.grid_text.insert("1.0", grid_text)

            self.current_grid_data = extracted_grid
            self.render_grid(extracted_grid)

            self.status_label.config(
                text=f"Detected {detected_rows} rows x {detected_cols} columns. Please check OCR output.",
                fg="blue"
            )

            messagebox.showinfo(
                "Grid Extracted",
                f"Detected grid size: {detected_rows} rows x {detected_cols} columns.\n\n"
                "Please review and correct any '?' characters before running the benchmark."
            )

        except Exception as e:
            self.status_label.config(text="Image extraction failed.", fg="red")
            messagebox.showerror("Image Extraction Error", str(e))

    def clear_results(self):
        # Remove all rows from results table
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        # Re-render current grid if available
        if self.current_grid_data:
            self.render_grid(self.current_grid_data)

        # Reset path information label
        self.path_label.config(text="Select a successful result to view its path.")

        # Update application status
        self.status_label.config(text="Results cleared.", fg="green")

    def save_current_input(self):
        # Create results directory if it does not exist
        os.makedirs("results", exist_ok=True)

        # Retrieve current grid and word inputs
        grid_content = self.grid_text.get("1.0", tk.END).strip()
        words_content = self.words_entry.get().strip()

        # Save current inputs to text file
        with open("results/current_input.txt", "w", encoding="utf-8") as file:
            file.write("GRID:\n")
            file.write(grid_content)
            file.write("\n\nWORDS:\n")
            file.write(words_content)

        # Display save confirmation message
        messagebox.showinfo("Saved", "Current grid and word list saved to results/current_input.txt")

    def open_results_folder(self):
        # Use current experiment folder if one exists
        if hasattr(self, "current_experiment_dir") and self.current_experiment_dir:
            results_path = os.path.abspath(self.current_experiment_dir)
        else:
            # Fall back to general results folder
            results_path = os.path.abspath("results")

        # Create results folder if it does not exist
        if not os.path.exists(results_path):
            os.makedirs(results_path)

        try:
            # Open folder in Windows file explorer
            os.startfile(results_path)
        except AttributeError:
            # Show folder path on system 
            messagebox.showinfo("Results Folder", results_path)

    def update_graph_preview(self, event=None):
        # Stop if no benchmark results exist
        if self.latest_df is None:
            return

        # Get selected metric for graph
        metric = self.graph_metric.get()

        # Clear previous graph preview
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Calculate average metric value for each algorithm
        grouped = (
            self.latest_df
            .groupby("algorithm")[metric]
            .mean()
            .sort_values()
        )

        # Create graph figure
        fig = Figure(figsize=(8.5, 5.2), dpi=100)

        # Add chart area to figure
        ax = fig.add_subplot(111)

        # Draw bar chart
        grouped.plot(kind="bar", ax=ax)

        # Set graph title
        ax.set_title(f"Average {metric.replace('_', ' ').title()}")

        # Label x axis
        ax.set_xlabel("Algorithm")

        # Label y axis
        ax.set_ylabel(metric.replace("_", " ").title())

        # Rotate x axis labels for readability
        ax.tick_params(axis="x", rotation=35)

        # Adjust spacing around graph
        fig.tight_layout()

        # Embed graph inside tkinter frame
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)

        # Render graph canvas
        self.graph_canvas.draw()

        # Display graph in GUI
        self.graph_canvas.get_tk_widget().pack(fill="both", expand=True)

    def generate_report(self):
        # Stop if no benchmark results exist
        if self.latest_df is None:
            messagebox.showwarning("No Results", "Run a benchmark before generating a report.")
            return

        # Stop if no experiment folder exists
        if not self.current_experiment_dir:
            messagebox.showwarning("No Experiment", "No experiment folder found.")
            return

        try:
            # Retrieve current target words
            words = self.get_words_input()

            # Create report generator for current experiment
            report_generator = ReportGenerator(self.current_experiment_dir)

            # Generate text report
            report_path = report_generator.generate_txt_report(
                self.latest_df,
                self.current_grid_data,
                words
            )

            # Show report generation confirmation
            messagebox.showinfo(
                "Report Generated",
                f"Report generated successfully:\n\n{report_path}"
            )

            # Update application status
            self.status_label.config(
                text=f"Report generated: {report_path}",
                fg="green"
            )

        except Exception as e:
            # Show report generation error information
            messagebox.showerror("Report Error", str(e))


def main():
    # Create main tkinter window
    root = tk.Tk()

    # Start application
    WordSearchAIApp(root)

    # Run tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()