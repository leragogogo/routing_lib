import csv
from .core import Graph
from .utils import apply_component_strategy


def load_graph_from_csv(
        node_file_path: str,
        edge_file_path: str,
        directed: bool = True,
        strategy: str = 'all',
) -> Graph:
    """
    Load a graph from two CSV files: one for nodes and one for edges.

    :param node_file_path: Path to the CSV file with nodes (must include 'id')
    :param edge_file_path: Path to the CSV file with edges (must include 'from', 'to', 'cost')
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

    # Load nodes
    with open(node_file_path, newline='', encoding="utf-8") as node_file:
        reader = csv.DictReader(node_file)
        for row in reader:
            node_id = row["id"]
            attrs = {k: v for k, v in row.items() if k != "id"}
            # Convert attribute values to float if possible (lat, lon)
            for key, value in attrs.items():
                try:
                    attrs[key] = float(value)
                except ValueError:
                    pass
            graph.add_node(node_id, **attrs)

    # Load edges
    with open(edge_file_path, newline='', encoding="utf-8") as edge_file:
        reader = csv.DictReader(edge_file)
        for row in reader:
            from_id = row["from"]
            to_id = row["to"]
            cost = float(row["cost"])
            graph.add_edge(from_id, to_id, cost)

    return apply_component_strategy(graph, strategy)
