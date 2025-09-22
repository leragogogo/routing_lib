import numpy as np


def tsp_nn(
        stops: list[str],
        distances: np.ndarray,
        node_to_index: dict[str, int],
        start: str,
        return_to_start: bool = False
) -> tuple[list[str], float]:
    """
    Nearest Neighbor heuristic for the Traveling Salesman Problem (TSP).

    Uses a precomputed distance matrix where distances[i, j] is the shortest-path
    distance between stops[i] and stops[j]. Greedily picks the nearest
    unvisited stop at each step.

    Feasible for graphs with a couple of thousands nodes.

    :param stops: List of stop IDs.
    :param distances: NumPy (n x n) array of pairwise distances between stops.
                 dist[i, j] may be asymmetric (directed graphs). Must be >= 0 or inf.
    :param node_to_index: Dictionary of nodes and its corresponding index.
    :param start: ID of the starting stop (must be in `stops`).
    :param return_to_start: If True, closes the tour by returning to `start`.
    :return: (tour_ids, total_length)
             - tour_ids: visiting order as stop IDs (includes start twice if return_to_start=True)
             - total_length: total tour length
    :raises ValueError: if start not in stops, matrix shape mismatch,
                        or if some required node is unreachable (inf).
    """
    n = len(stops)

    if distances.shape != (n, n):
        raise ValueError(f"dist shape {distances.shape} does not match len(stops)={n}")

    if start not in node_to_index:
        raise ValueError(f"Start node {start!r} is not found in stops")

    start_idx = node_to_index[start]
    # Keep track of visited stops
    visited = np.zeros(n, dtype=bool)
    # Order of visited stops
    tour_idx: list[int] = [start_idx]

    total_length = 0.0
    current = start_idx
    visited[current] = True

    for _ in range(n - 1):
        # Distances from current stop
        row = distances[current].copy()
        # Mark visited stop's distance as inf so that it won't be chosen again
        row[visited] = np.inf
        # Find the nearest stop
        next_idx = int(np.argmin(row))
        # Find the nearest stop's distance
        next_cost = row[next_idx]

        if np.isinf(next_cost):
            # No reachable unvisited nodes remain → disconnected stop set
            remaining = [stops[i] for i in range(n) if not visited[i]]
            raise ValueError(
                f"No reachable next stop from {stops[current]!r}. Unvisited: {remaining}"
            )
        # Increment the total length
        total_length += next_cost
        # Move to the next stop
        current = next_idx
        # Mark that current stop is visited
        visited[current] = True
        # Expand tour
        tour_idx.append(current)

    # Add the way back to the start stop if it was specified
    if return_to_start:
        back_cost = distances[current, start_idx]
        if np.isinf(back_cost):
            raise ValueError(f"Cannot return to start {start!r} from {stops[current]!r} (unreachable).")
        total_length += back_cost
        tour_idx.append(start_idx)

    # Extract stops ids based on indexes
    tour_ids = [stops[i] for i in tour_idx]

    return tour_ids, total_length
