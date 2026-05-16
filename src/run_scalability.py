from src.scalability_benchmark import ScalabilityBenchmark
from src.visualiser import ResultVisualiser

def main():
    words = ["CAT", "DOG", "BIRD", "FISH", "HOUSE"]

    grid_sizes = [5, 8, 10, 12, 15]

    benchmark = ScalabilityBenchmark()
    df = benchmark.run(
        grid_sizes=grid_sizes,
        words=words,
        repetitions=5
    )

    visualiser = ResultVisualiser()
    visualiser.plot_scalability(df, "execution_time_ms", "scalability_time.png")
    visualiser.plot_scalability(df, "nodes_expanded", "scalability_nodes.png")
    visualiser.plot_scalability(df, "states_generated", "scalability_states.png")
    visualiser.plot_scalability(df, "max_frontier_size", "scalability_frontier.png")

    print("\nScalability benchmark complete.")


if __name__ == "__main__":
    main()