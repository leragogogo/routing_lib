class Node:
    """
    A node in the graph.

    Stores its ID, attributes, and neighboring nodes with edge costs.
    """

    def __init__(self, id: str, attrs: dict):
        """
        Initialize a node.

        :param id: Unique identifier of the node.
        :param attrs: Dictionary of node attributes (e.g., lat, lon, name).
        """
        self.id: str = id
        self.attrs: dict = attrs
        self.neighbours: dict[str, float] = {}

    def add_neighbour(self, neighbour_id: str, cost: float) -> None:
        """
        Add a neighbor node with the given cost.

        :param neighbour_id: ID of the neighboring node.
        :param cost: Cost of the edge to the neighbor.
        :return: None
        """
        self.neighbours[neighbour_id] = cost

    def get_neighbours(self) -> dict[str, float]:
        """
        Get all neighboring nodes with edge costs.

        :return: Dictionary of neighbor IDs and their edge costs.
        """
        return self.neighbours

    def get_id(self) -> str:
        """
        Get the node's ID.

        :return: Node ID as a string.
        """
        return self.id

    def get_attrs(self) -> dict:
        """
        Get the node's attributes.

        :return: Dictionary of attributes.
        """
        return self.attrs


class Graph:
    """
    A graph consisting of nodes and edges.

    Supports both directed and undirected graphs.
    """

    def __init__(self, directed: bool = True):
        """
        Initialize an empty graph.

        :param directed: Whether the graph is directed (default: True).
        :return: None
        """
        self.nodes: dict[str, Node] = {}
        self.directed: bool = directed

    def add_node(self, node_id: str, **attrs: dict) -> None:
        """
        Add a node to the graph if it doesn't already exist.

        :param node_id: Unique identifier of the node.
        :param attrs: Arbitrary attributes passed as keyword arguments.
        :return: None
        """
        if not self.has_node(node_id):
            self.nodes[node_id] = Node(node_id, attrs)

    def add_edge(self, from_id: str, to_id: str, cost: float) -> None:
        """
        Add an edge between two nodes (creates nodes if needed).

        :param from_id: ID of the starting node.
        :param to_id: ID of the target node.
        :param cost: Cost of the edge.
        :return: None
        """
        self.add_node(from_id)
        self.add_node(to_id)
        self.nodes[from_id].add_neighbour(to_id, cost)
        if not self.directed:
            self.nodes[to_id].add_neighbour(from_id, cost)

    def get_node(self, node_id: str) -> Node:
        """
        Get a node object by its ID.

        :param node_id: ID of the node.
        :return: Node object.
        """
        return self.nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.

        :param node_id: ID of the node to check.
        :return: True if node exists, False otherwise.
        """
        return node_id in self.nodes

    def set_node_attr(self, node_id: str, attr_name: str, attr: any):
        """
        Set a new attr for a node
        :param node_id: ID of the node to set a new attr.
        :param attr_name: Name of a new attr.
        :param attr: Value of a new attr.
        :raise ValueError: If a node was not found.
        """
        if self.has_node(node_id):
            node = self.get_node(node_id)
            node.attrs[attr_name] = attr
            return

        raise ValueError(f'Node: {node_id} not found')

    def get_all_nodes(self) -> list[Node]:
        """
        Get all nodes in the graph.

        :return: List of Node objects.
        """
        return list(self.nodes.values())

    def get_neighbours(self, id: str) -> dict[str, float]:
        """
        Get all neighbours of a given node.

        :param id: ID of the node.
        :return: Dictionary of neighbor IDs and edge costs.
        """
        return self.nodes[id].get_neighbours()

    def get_edge_cost(self, from_id: str, to_id: str) -> float:
        """
        Get the cost of the edge from one node to another.

        :param from_id: ID of the source node.
        :param to_id: ID of the destination node.
        :return: Cost of the edge if it exists, otherwise float('inf').
        """
        if self.has_node(from_id):
            neighbours = self.get_neighbours(from_id)
            if to_id in neighbours:
                return neighbours[to_id]
        return float("inf")
