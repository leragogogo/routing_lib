import numpy as np


def tsp_held_karp(
        distances: np.ndarray,
        index_to_node: dict[int, str],
) -> tuple[list[str], float]:
    """
    Held-Karp algorithm (DP with bitmasks) for TSP.
    Finds the exact optimal tour.

    Feasible only for small graphs(n <= 20)

    :param distances: NumPy (n x n) array of pairwise distances between stops.
                 dist[i, j] may be asymmetric (directed graphs). Must be >= 0 or inf.
    :param index_to_node: Dictionary of indexes and its corresponding nodes.
    :return: (tour_ids, optimal_length)
            - tour_ids: visiting order as stop IDs
            - optimal_length: optimal tour length
    """
    n = len(distances)

    # DP[mask][j] = min cost to reach subset mask, ending at j
    DP = {(1 << 0, 0): 0}

    # Parent pointers for tour reconstruction
    parent = {}

    for mask in range(1 << n):
        # Must include start node (0)
        if not (mask & 1):
            continue
        for j in range(n):
            # j not in mask
            if not (mask & (1 << j)):
                continue

            prev_mask = mask ^ (1 << j)
            if prev_mask == 0:
                continue

            best_cost = float('inf')
            best_index = -1

            for i in range(n):
                if not (prev_mask & (1 << i)):
                    continue
                cost = DP.get((prev_mask, i), float('inf')) + distances[i][j]
                if cost < best_cost:
                    best_cost = cost
                    best_index = i

            DP[(mask, j)] = best_cost
            parent[(mask, j)] = (prev_mask, best_index)

    # Return to start node
    full_mask = (1 << n) - 1
    optimal_length = float('inf')
    best_index = -1
    for i in range(1, n):
        cost = DP[(full_mask, i)] + distances[i][0]
        if cost < optimal_length:
            optimal_length = cost
            best_index = i

    # Reconstruct the tour
    tour = [0]
    mask = full_mask
    j = best_index
    while j != 0:
        tour.append(j)
        mask, j = parent[(mask, j)]

    tour.append(0)
    tour.reverse()

    # Transform indexes into nodes ids
    tour_ids = []
    for i in tour:
        tour_ids.append(index_to_node[i])

    return tour_ids, optimal_length



