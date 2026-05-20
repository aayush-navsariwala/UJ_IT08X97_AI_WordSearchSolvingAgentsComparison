import os
import pandas as pd

class ReportGenerator:
    def __init__(self, experiment_dir: str):
        # Store experiment folder path
        self.experiment_dir = experiment_dir

    def generate_txt_report(self, df: pd.DataFrame, grid_data, words):
        # Create output path for report
        report_path = os.path.join(self.experiment_dir, "experiment_report.txt")

        # Find fastest recorded result
        best_time = df.sort_values("execution_time_ms").iloc[0]

        # Find result with fewest expanded nodes
        best_nodes = df.sort_values("nodes_expanded").iloc[0]

        # Find result with smallest maximum frontier size
        best_frontier = df.sort_values("max_frontier_size").iloc[0]

        # Calculate success rate for every algorithm
        success_rate = (
            df.groupby("algorithm")["success"]
            .mean()
            .mul(100)
            .round(2)
            .reset_index()
        )

        # Write report content to text file
        with open(report_path, "w", encoding="utf-8") as file:
            file.write("AI WORD SEARCH ALGORITHM COMPARISON REPORT\n")
            file.write("=" * 55 + "\n\n")

            file.write("1. Experiment Overview\n")
            file.write("-" * 25 + "\n")
            file.write(f"Grid size: {len(grid_data)} x {len(grid_data[0])}\n")
            file.write(f"Target words: {', '.join(words)}\n\n")

            file.write("Grid Used:\n")

            # Write grid used in experiment
            for row in grid_data:
                file.write(" ".join(row) + "\n")

            file.write("\n2. Algorithms Compared\n")
            file.write("-" * 25 + "\n")
            file.write("Depth-First Search\n")
            file.write("Breadth-First Search\n")
            file.write("Iterative Deepening Depth-First Search\n")
            file.write("Greedy Best-First Search\n")
            file.write("A* Search\n")
            file.write("Beam Search\n\n")

            file.write("3. Metrics Recorded\n")
            file.write("-" * 25 + "\n")
            file.write("Execution time in milliseconds\n")
            file.write("Nodes expanded\n")
            file.write("States generated\n")
            file.write("Maximum frontier size\n")
            file.write("Success status\n")
            file.write("Path length\n\n")

            file.write("4. Key Findings\n")
            file.write("-" * 25 + "\n")

            # Write fastest result
            file.write(
                f"Fastest result: {best_time['algorithm']} for word {best_time['word']} "
                f"with {best_time['execution_time_ms']:.3f} ms.\n"
            )

            # Write result with fewest expanded nodes
            file.write(
                f"Lowest node expansion: {best_nodes['algorithm']} for word {best_nodes['word']} "
                f"with {best_nodes['nodes_expanded']} nodes expanded.\n"
            )

            # Write result with smallest frontier size
            file.write(
                f"Lowest maximum frontier size: {best_frontier['algorithm']} for word {best_frontier['word']} "
                f"with frontier size {best_frontier['max_frontier_size']}.\n\n"
            )

            file.write("5. Success Rate by Algorithm\n")
            file.write("-" * 25 + "\n")

            # Write average success rate for every algorithm
            for _, row in success_rate.iterrows():
                file.write(f"{row['algorithm']}: {row['success']}%\n")

            file.write("\n6. Full Results\n")
            file.write("-" * 25 + "\n")

            # Write complete benchmark table
            file.write(df.to_string(index=False))

            file.write("\n\n7. Generated Graphs\n")
            file.write("-" * 25 + "\n")
            file.write("Graphs are stored inside the experiment graphs folder.\n")

        return report_path