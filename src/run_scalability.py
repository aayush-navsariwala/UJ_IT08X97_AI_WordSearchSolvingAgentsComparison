from src.scalability_benchmark import ScalabilityBenchmark
from src.visualiser import ResultVisualiser

def main():
    # Define target words used in benchmark
    words = ["CAT", "DOG", "BIRD", "FISH", "HOUSE"]

    # Define grid sizes for scalability testing
    grid_sizes = [5, 8, 10, 12, 15]

    # Create scalability benchmark runner
    benchmark = ScalabilityBenchmark()

    # Execute scalability benchmark across all grid sizes
    df = benchmark.run(
        grid_sizes=grid_sizes,
        words=words,
        repetitions=5
    )

    # Create graph visualiser
    visualiser = ResultVisualiser()

    # Generate execution time graph
    visualiser.plot_scalability(df, "execution_time_ms", "scalability_time.png")

    # Generate node expansion graph
    visualiser.plot_scalability(df, "nodes_expanded", "scalability_nodes.png")

    # Generate generated states graph
    visualiser.plot_scalability(df, "states_generated", "scalability_states.png")

    # Generate frontier size graph
    visualiser.plot_scalability(df, "max_frontier_size", "scalability_frontier.png")

    # Display completion message
    print("\nScalability benchmark complete.")


# Run program only if this file is executed directly
if __name__ == "__main__":
    main()