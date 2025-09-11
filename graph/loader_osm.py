import xml.etree.ElementTree as ET
from .core import Graph
from .utils import haversine,apply_component_strategy
from typing import Callable


def get_builtin_way_filter(filter_name: str) -> Callable[[dict], bool]:
    """
    Return a predefined way filter function based on the given filter name.

    :param filter_name: One of 'driveable', 'pedestrian', 'bicycle'
    :return: A callable that filters OSM way tags
    :raises ValueError: If the filter_name is not recognized
    """
    if filter_name == "driveable":
        valid = {
            "motorway", "trunk", "primary", "secondary", "tertiary",
            "residential", "unclassified", "service",
            "living_street", "road",
            "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link",
        }
        return lambda tags: tags.get("highway") in valid

    elif filter_name == "pedestrian":
        valid = {
            "footway", "path", "pedestrian", "steps",
            "crossing", "platform", "corridor", "living_street",
        }
        return lambda tags: tags.get("highway") in valid

    elif filter_name == "bicycle":
        valid = {
            "cycleway", "path", "track",
            "residential", "unclassified", "service", "living_street", "road",
            "tertiary", "secondary",
        }
        return lambda tags: tags.get("highway") in valid

    else:
        raise ValueError(f"Unknown filter_name: {filter_name}")


def load_graph_from_osm_xml(
        filepath: str,
        directed: bool = False,
        filter_name: str = None,
        way_filter: Callable[[dict], bool] = None,
        strategy: str = 'all',
) -> Graph:
    """
    Load a graph from an OSM XML (.osm) file.
    :param filepath: Path to the .osm XML file.
    :param directed: Whether the graph should be directed (default: False).
    :param filter_name: Optional predefined filter to select which ways are included.
                        Valid values:
                          - "driveable": Includes motorways, trunks, primary/secondary/tertiary, residential, service.
                          - "pedestrian": Includes footways, pedestrian zones, paths, and steps.
                          - "bicycle": Includes cycleways, tracks, and paths suitable for bikes.
                        If both `filter_name` and `way_filter` are None, all ways are included.
    :param way_filter: Optional custom filter function.
                       A callable that takes a dictionary of OSM tags (`dict[str, str]`)
                       and returns `True` if the way should be included, or `False` to skip it.
                       This takes precedence over `filter_name` if provided.
    :param strategy: Optional strategy for handling disconnected components in the graph.
                               Valid values:
                                 - "all" (default): Keep all components as-is.
                                 - "largest": Keep only the largest connected component.
                                 - "label": Keep all components, but add a `component_id`
                                            attribute to each node indicating its component.
                               Use "largest" for typical routing tasks to ensure a connected network,
                               or "label" for analysis/visualization.
    :return: Graph object.
    """
    graph = Graph(directed=directed)

    # All nodes
    node_data: dict[str, dict] = {}

    # Determine built-in filter if applicable
    if way_filter is None and filter_name:
        way_filter = get_builtin_way_filter(filter_name)

    tree = ET.parse(filepath)
    root = tree.getroot()

    # Extract all nodes
    for elem in root.findall("node"):
        node_id = elem.attrib["id"]
        # Start with all attributes (lat, lon, uid, etc.)
        attrs = {k: v for k, v in elem.attrib.items() if k != "id"}

        # Include tags as key-value pairs
        for tag in elem.findall("tag"):
            k = tag.attrib.get("k")
            v = tag.attrib.get("v")
            if k and v:
                attrs[k] = v

        # Convert lat/lon to float if present
        if "lat" in attrs:
            attrs["lat"] = float(attrs["lat"])
        if "lon" in attrs:
            attrs["lon"] = float(attrs["lon"])

        node_data[node_id] = attrs

    filtered_nodes: set[str] = set()
    edges: list[tuple[str,str]] = []

    # Extract and filter ways. Identify only filtered nodes
    for way in root.findall("way"):
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in way.findall("tag")}

        if way_filter and not way_filter(tags):
            continue  # Skip this way if it doesn't match

        node_refs = [nd.attrib["ref"] for nd in way.findall("nd")]

        for i in range(len(node_refs) - 1):
            from_id = node_refs[i]
            to_id = node_refs[i + 1]

            edges.append((from_id, to_id))
            filtered_nodes.add(from_id)
            filtered_nodes.add(to_id)

    # Dict with lat and lon af each filtered node
    node_coords: dict[str, tuple[float, float]] = {}

    # Add filtered nodes to a graph
    for node_id in filtered_nodes:
        attrs = node_data.get(node_id, {})
        graph.add_node(node_id, **attrs)

        lat = attrs.get("lat")
        lon = attrs.get("lon")
        if lat is not None and lon is not None:
            node_coords[node_id] = (lat, lon)

    # Add filtered edges to a graph
    for from_id, to_id in edges:
        if from_id in node_coords and to_id in node_coords:
            lat1, lon1 = node_coords[from_id]
            lat2, lon2 = node_coords[to_id]
            cost = haversine(lat1, lon1, lat2, lon2)
        else:
            # Use fallback cost if coordinates are missing
            cost = None

        graph.add_edge(from_id, to_id, cost)

    return apply_component_strategy(graph, strategy)
