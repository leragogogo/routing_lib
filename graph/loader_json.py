import json
from .core import Graph
from .utils import apply_component_strategy


def load_graph_from_json(
        filepath: str,
        directed: bool = True,
        strategy: str = 'all',
) -> Graph:
    """
    Load a graph from a JSON file.

    :param filepath: Path to the JSON file
    :param directed: Whether the graph is directed
    :param strategy: Optional strategy for handling disconnected components in the graph.
                               Valid values:
                                 - "all" (default): Keep all components as-is.
                                 - "largest": Keep only the largest connected component.
                                 - "label": Keep all components, but add a `component_id`
                                            attribute to each node indicating its component.
                               Use "largest" for typical routing tasks to ensure a connected network,
                               or "label" for analysis/visualization.
    :return: Graph object
    """
    graph = Graph(directed=directed)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Add nodes
    for node in data.get("nodes", []):
        node_id = node["id"]
        attrs = {k: v for k, v in node.items() if k != "id"}
        graph.add_node(node_id, **attrs)

    # Add edges
    for edge in data.get("edges", []):
        from_id = edge["from"]
        to_id = edge["to"]
        cost = float(edge["cost"])
        graph.add_edge(from_id, to_id, cost)

    return apply_component_strategy(graph, strategy)
