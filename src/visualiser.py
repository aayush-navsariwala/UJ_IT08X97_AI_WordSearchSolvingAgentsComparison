import os
import matplotlib.pyplot as plt
import pandas as pd

class ResultVisualiser:
    def __init__(self, output_dir: str = "results/graphs"):
        # Store output directory for generated graphs
        self.output_dir = output_dir

        # Create output directory 
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_metric_by_algorithm(self, df: pd.DataFrame, metric: str, filename: str):
        # Calculate average metric value for every algorithm
        grouped = df.groupby("algorithm")[metric].mean().sort_values()

        # Create graph figure
        plt.figure(figsize=(8, 5))

        # Generate a bar chart for selected metric
        grouped.plot(kind="bar")

        # Set graph title
        plt.title(f"Average {metric.replace('_', ' ').title()} by Algorithm")

        # Label y axis
        plt.ylabel(metric.replace("_", " ").title())

        # Label x axis
        plt.xlabel("Algorithm")

        # Adjust layout spacing automatically
        plt.tight_layout()

        # Save graph to output directory
        plt.savefig(os.path.join(self.output_dir, filename))

        # Close graph to free memory
        plt.close()

    def plot_scalability(self, df: pd.DataFrame, metric: str, filename: str):
        # Calculate average metric value by grid size and algorithm
        grouped = df.groupby(["grid_size", "algorithm"])[metric].mean().reset_index()

        # Create graph figure
        plt.figure(figsize=(9, 6))

        # Plot scalability line for every algorithm
        for algorithm in grouped["algorithm"].unique():
            subset = grouped[grouped["algorithm"] == algorithm]

            plt.plot(
                subset["grid_size"],
                subset[metric],
                marker="o",
                label=algorithm
            )

        # Set graph title
        plt.title(f"{metric.replace('_', ' ').title()} by Grid Size")

        # Label x axis
        plt.xlabel("Grid Size")

        # Label y axis
        plt.ylabel(metric.replace("_", " ").title())

        # Display graph legend
        plt.legend()

        # Adjust layout spacing automatically
        plt.tight_layout()

        # Save graph to output directory
        plt.savefig(os.path.join(self.output_dir, filename))

        # Close graph to free memory
        plt.close()