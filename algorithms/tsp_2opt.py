import numpy as np


def tsp_2opt(
        distances: np.ndarray,
        node_to_index: dict[str, int],
        tour_ids: list[str],
        tour_length: float,
) -> tuple[list[str], float]:
    """
    2-opt local search for TSP tours.

    Uses a precomputed distance matrix where distances[i, j] is the shortest-path
    distance between stops[i] and stops[j] and optimize the already found tour.

    Feasible for graphs with approximately up to 50 nodes.

    :param distances: NumPy (n x n) array of pairwise distances between stops.
                 dist[i, j] may be asymmetric (directed graphs). Must be >= 0 or inf.
    :param node_to_index: Dictionary of nodes and its corresponding index.
    :param tour_ids: Previously found tour that needs to be optimized.
    :param tour_length: Length of previously found tour that needs to be optimized.
    :raise ValueError: if the input tour has < 4 distinct nodes.
    :return: (tour_ids, total_length)
             - tour_ids: improved visiting order as stop IDs
             - total_length: improved total tour length
    """
    if len(tour_ids) < 4:
        raise ValueError("2-opt requires a tour with at least 3 edges.")

    # Identify if the tour is opened or cycled
    is_cycled = tour_ids[0] == tour_ids[-1]

    best = tour_ids[:]
    best_length = tour_length
    improved = True
    n = len(best)

    while improved:
        improved = False
        for i in range(1, n - 2):
            # First edge for possible swap
            a, b = best[i - 1], best[i]
            index_a, index_b = node_to_index[a], node_to_index[b]

            for j in range(i + 1, n - 1):
                # Second edge for possible swap
                c = best[j]
                # The last node is the start node in cycled tour
                d = best[(j + 1) % n] if is_cycled else best[j + 1]
                index_c, index_d = node_to_index[c], node_to_index[d]

                # Skip if the edges are adjacent
                if a == c or b == d:
                    continue

                # Calculate cost before and after swiping
                old_cost = distances[index_a, index_b] + distances[index_c, index_d]
                new_cost = distances[index_a, index_c] + distances[index_b, index_d]

                if new_cost < old_cost:
                    # Reverse segment [i...j] to perform 2opt swap
                    best = best[:i] + best[i: j + 1][:: -1] + best[j + 1:]
                    best_length += (new_cost - old_cost)
                    improved = True
                    break

            if improved:
                break

    return best, best_length
