import json
from graph.core import Graph
from graph.utils import apply_component_strategy
from .loader import AbstractLoader, LoadOptions, JSONSource


class JSONLoader(AbstractLoader):
    """
    JSON Loader to build a graph from a json file
    """
    def load(self, source: JSONSource, options: LoadOptions) -> Graph:
        """
        Load a graph from a JSON file.

        Nodes must include id. Edges must include from, to, cost.

        :param source: JSONSource:
            A data source containing:
                - filepath: Path to the JSOM file with graph.

        :param options: LoadOptions:
            Controls graph loading behavior:
                - directed (bool): Whether the graph is directed.
                - strategy (str): Optional strategy for handling disconnected components in the graph.
                    "all" (default): Keep all components.
                    "largest": Keep only the largest connected component.
                    "label": Keep all components but add a `component_id` attribute to each node.
                    Use "largest" for typical routing tasks to ensure a connected network,
                    or "label" for analysis/visualization.
        :return: Graph object
        """
        graph = Graph(directed=options.directed)

        with open(source.filepath, "r", encoding="utf-8") as f:
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

        return apply_component_strategy(graph, options.strategy)
