import xml.etree.ElementTree as ET
from .core import Graph
from .utils import haversine
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
            "residential", "unclassified", "service"
        }
        return lambda tags: tags.get("highway") in valid

    elif filter_name == "pedestrian":
        valid = {"footway", "path", "pedestrian", "steps"}
        return lambda tags: tags.get("highway") in valid

    elif filter_name == "bicycle":
        valid = {"cycleway", "path", "track"}
        return lambda tags: tags.get("highway") in valid

    else:
        raise ValueError(f"Unknown filter_name: {filter_name}")


def load_graph_from_osm_xml(
        filepath: str,
        directed: bool = False,
        filter_name: str = None,
        way_filter: Callable[[dict], bool] = None
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
    :return: Graph object.
    """
    graph = Graph(directed=directed)
    # Node coords to calculate haversine distance
    node_coords = {}

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

        graph.add_node(node_id, **attrs)
        if "lat" in attrs and "lon" in attrs:
            node_coords[node_id] = (attrs["lat"], attrs["lon"])

    # Extract ways and filter them
    for way in root.findall("way"):
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in way.findall("tag")}

        if way_filter and not way_filter(tags):
            continue  # Skip this way if it doesn't match

        node_refs = [nd.attrib["ref"] for nd in way.findall("nd")]

        for i in range(len(node_refs) - 1):
            from_id = node_refs[i]
            to_id = node_refs[i + 1]

            # Add missing nodes if not already present
            if not graph.has_node(from_id):
                graph.add_node(from_id)
            if not graph.has_node(to_id):
                graph.add_node(to_id)

            # If both have coordinates, calculate real distance
            if from_id in node_coords and to_id in node_coords:
                lat1, lon1 = node_coords[from_id]
                lat2, lon2 = node_coords[to_id]
                cost = haversine(lat1, lon1, lat2, lon2)
            else:
                # Use fallback cost if coordinates are missing
                cost = None

            graph.add_edge(from_id, to_id, cost)

    return graph
