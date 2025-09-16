import heapq
from graph.core import Graph


def dijkstra(
        graph: Graph,
        source: str,
        target: str = None
) -> tuple[dict[str, float], dict[str, str]]:
    """
    Dijkstra's algorithm for the single-source shortest paths.

    :param graph: Graph object
    :param source: Starting node ID.
    :param target: Optional target node ID. If given, the search stops early when reached.
    :return:
    """
    distances: dict[str, float] = {node: float("inf") for node in graph.nodes}
    distances[source] = 0.0

    # Predecessor map for path reconstruction
    prev: dict[str, str] = {node: None for node in graph.nodes}

    # Priority queue of (distance, node)
    pq: list[tuple[float, str]] = [(0.0, source)]

    while pq:
        current_distance, u = heapq.heappop(pq)

        # Skip this outdated entry(in heapq we can't remove value based on the node_id)
        if current_distance > distances[u]:
            continue

        # Finish the execution if we reached the target
        if target is not None and u == target:
            break

        for v in graph.get_node(u).neighbours:
            cost = graph.get_edge_cost(u, v)
            if cost is None:
                continue
            new_cost = current_distance + cost
            # Update distance if shorter is found
            if new_cost < distances[v]:
                distances[v] = new_cost
                prev[v] = u
                heapq.heappush(pq, (new_cost, v))

    return distances, prev


def reconstruct_path(
        prev: dict[str, str],
        source: str,
        target: str
) -> list[str]:
    """
    Reconstruct the shortest path from source to target.

    :param prev: dict[node_id] -> predecessor
    :param source: source node ID
    :param target: target node ID
    :return: List of node IDs representing the path
    """
    # If target is the source, trivial path
    if target == source:
        return [source]

    # If target not discovered at all, unreachable
    if target not in prev or prev[target] is None:
        return []

    path: list[str] = []
    current = target
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = prev[current]

    path.reverse()

    return path
