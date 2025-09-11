from math import radians, sin, cos, sqrt, atan2
from .core import Graph
from collections import deque


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    :param lat1: Latitude of point 1 in decimal degrees.
    :param lon1: Longitude of point 1 in decimal degrees.
    :param lat2: Latitude of point 2 in decimal degrees.
    :param lon2: Longitude of point 2 in decimal degrees.
    :return: Distance in kilometers.
    """
    R = 6371.0  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def connected_components(graph: Graph) -> list[set[str]]:
    """
    Extract all connected components.
    :param graph: Graph object
    :return: List of node sets, each a connected component
    """
    seen: set[str] = set()  # Tracks nodes we've already assigned to a component
    components: list[set[str]] = []  # Stores the final list of components

    # Loop over every node in the graph
    for start in graph.nodes:
        if start in seen:
            continue
        component = {start}
        seen.add(start)

        # Initialize BFS queue with this start node
        q = deque([start])

        # Explore the graph breadth-first
        while q:
            node = q.popleft()

            # Look at all neighbors of the current node
            for neighbour in graph.get_node(node).neighbours:
                # If neighbor not yet visited, add to this component
                if neighbour not in seen:
                    seen.add(neighbour)
                    component.add(neighbour)
                    q.append(neighbour)

        # After BFS finishes, we've discovered one full component
        components.append(component)

    return components


def extract_component(graph: Graph, component: set[str]) -> Graph:
    """
    Extract the component from a graph.
    :param graph: Graph object
    :param component: Component of a graph that is needed to be extracted.
    :return Graph object
    """
    final_graph = Graph(graph.directed)

    # Extract nodes
    for node_id in component:
        attr = graph.get_node(node_id).get_attrs()
        final_graph.add_node(node_id, **attr)

    # Extract edges
    for node_id in component:
        for neighbour_id in graph.get_node(node_id).neighbours:
            cost = graph.get_edge_cost(node_id, neighbour_id)
            final_graph.add_edge(node_id, neighbour_id, cost)

    return final_graph


def apply_component_strategy(graph: Graph, strategy: str = 'all') -> Graph:
    """
    Apply strategy for handling disconnected components in the graph.
    :param graph: Graph object
    :param strategy: Valid values:
                    - "all" (default): Keep all components as-is.
                    - "largest": Keep only the largest connected component.
                    - "label": Keep all components, but add a `component_id`
                            attribute to each node indicating its component.
                    Use "largest" for typical routing tasks to ensure a connected network,
                    or "label" for analysis/visualization.
    :return: Graph object
    :raise ValueError: If the strategy is not recognized
    """
    if strategy == 'all':
        return graph
    elif strategy == 'largest':
        components = connected_components(graph)
        largest = max(components, key=len)
        return extract_component(graph, largest)
    elif strategy == 'label':
        components = connected_components(graph)
        for component_id, component in enumerate(components):
            for node in component:
                graph.set_node_attr(node, 'component_id', component_id)
        return graph
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
