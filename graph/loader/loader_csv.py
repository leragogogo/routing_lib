import csv
from graph.core import Graph
from graph.utils import apply_component_strategy
from .loader import AbstractLoader, LoadOptions, CSVSource


class CSVLoader(AbstractLoader):
    """
    CSV Loader to build a graph from to csv files(node.csv; edge.csv)
    """
    def load(self, source: CSVSource, options: LoadOptions) -> Graph:
        """
        Load a graph from two CSV files: one for nodes and one for edges.

        Nodes must include id. Edges must include from, to, cost.

        :param source: CSVSource:
            A data source containing:
                - nodes_filepath: Path to the CSV file with nodes (must include 'id').
                - edges_filepath: Path to the CSV file with edges (must include 'from', 'to', 'cost').
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

        # Load nodes
        with open(source.node_filepath, newline='', encoding="utf-8") as node_file:
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
        with open(source.edge_filepath, newline='', encoding="utf-8") as edge_file:
            reader = csv.DictReader(edge_file)
            for row in reader:
                from_id = row["from"]
                to_id = row["to"]
                cost = float(row["cost"])
                graph.add_edge(from_id, to_id, cost)

        return apply_component_strategy(graph, options.strategy)
