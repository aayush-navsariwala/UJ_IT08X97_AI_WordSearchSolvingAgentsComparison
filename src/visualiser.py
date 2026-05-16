import os
import matplotlib.pyplot as plt
import pandas as pd

class ResultVisualiser:
    def __init__(self, output_dir: str = "results/graphs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_metric_by_algorithm(self, df: pd.DataFrame, metric: str, filename: str):
        grouped = df.groupby("algorithm")[metric].mean().sort_values()

        plt.figure(figsize=(8, 5))
        grouped.plot(kind="bar")
        plt.title(f"Average {metric.replace('_', ' ').title()} by Algorithm")
        plt.ylabel(metric.replace("_", " ").title())
        plt.xlabel("Algorithm")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        
    def plot_scalability(self, df: pd.DataFrame, metric: str, filename: str):
        grouped = df.groupby(["grid_size", "algorithm"])[metric].mean().reset_index()

        plt.figure(figsize=(9, 6))

        for algorithm in grouped["algorithm"].unique():
            subset = grouped[grouped["algorithm"] == algorithm]
            plt.plot(subset["grid_size"], subset[metric], marker="o", label=algorithm)

        plt.title(f"{metric.replace('_', ' ').title()} by Grid Size")
        plt.xlabel("Grid Size")
        plt.ylabel(metric.replace("_", " ").title())
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()