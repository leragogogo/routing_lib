import numpy as np
from algorithms.dijkstra import dijkstra, reconstruct_path
from graph.core import Graph


def distance_matrix(
        graph: Graph,
        stops: list[str]
) -> tuple[np.ndarray, dict[str, int], dict[int,str], dict[tuple[str, str], list[str]]]:
    """
    Compute shortest path distances between all given stops.

    Runs Dijkstra from each stop and builds:
      - a dense NumPy distance matrix,
      - a node_to_index mapping from node IDs to matrix indexes,
      - index_to_node mapping from matrix indexes to node IDS,
      - a dictionary of reconstructed paths.

    :param graph: Graph object.
    :param stops: List of node IDs to include in the distance matrix.
    :return:
        matrix: np.ndarray (n x n) of shortest path distances.
                matrix[i, j] = shortest distance from stops[i] to stops[j].
                If unreachable, value is np.inf.
        node_to_index: dict[node_id -> int], maps node IDs to row/col indexes of the matrix.
        index_to_node: dict[int -> node_id], maps indexes of the matrix to node IDs to row/col.
        paths: dict[(source, target) -> list[str]], shortest path as a sequence of node IDs.
               Empty list if target is unreachable.
    """
    n = len(stops)
    matrix = np.full((n, n), np.inf, dtype=float)

    # Mapping nodes to indexes and vice versa
    node_to_index = {node: i for i, node in enumerate(stops)}
    index_to_node = {i: node for i, node in enumerate(stops)}

    # Path for each pair
    paths: dict[tuple[str, str], list[str]] = {}

    for source in stops:
        d, prev = dijkstra(graph, source)
        for target in stops:
            i, j = node_to_index[source], node_to_index[target]
            if source == target:
                matrix[i][j] = 0.0
            else:
                matrix[i][j] = d[target]
                paths[(source, target)] = reconstruct_path(prev, source, target)

    return matrix, node_to_index, index_to_node, paths
