from graph.core import Graph
import math
import numpy as np
from sklearn.neighbors import BallTree

EARTH_RADIUS_M = 6371008.8


def _gather_coords(
        graph: Graph,
        lat_key: str = "lat",
        lon_key: str = "lon",
) -> tuple[list[str], np.ndarray]:
    """
    Extract node IDs and (lat, lon) in *radians* from a Graph.
    Skips nodes missing lat/lon.

    :param graph: Graph object.
    :param lat_key: Name of the lat attribute.
    :param lon_key: Name of the lon attribute.
    :return: (ids, coord_rad)
             - ids: IDs of nodes of the given graph.
             - coords_rad: Coordinates of nodes of the given graph in radians.
    """
    ids: list[str] = []
    coords_rad: list[tuple[float, float]] = []

    for node in graph.get_all_nodes():
        attrs = node.get_attrs()
        if lat_key in attrs and lon_key in attrs:
            lat, lon = attrs[lat_key], attrs[lon_key]
            if lat is not None and lon is not None:
                ids.append(node.get_id())
                coords_rad.append((math.radians(lat), math.radians(lon)))

    return ids, np.array(coords_rad, dtype=float)


def closest_pair(
        graph1: Graph,
        graph2: Graph,
        lat_key: str = "lat",
        lon_key: str = "lon",
) -> tuple[str, str, float]:
    """
    Find the single closest pair of nodes (one from each graph) by geodesic distance.

    Uses a BallTree with metric='haversine'. Returns distance in meters.
    :param graph1: First graph object.
    :param graph2: Second graph object.
    :param lat_key: Name of the lat attribute.
    :param lon_key: Name of the lon attribute.
    :raises ValueError: If no geocoded nodes found in one of the graphs.
    :return: (id1, id2, best_distance_m)
             - id1: ID of the closest node from the first graph.
             - id2: ID of the closest node from the second graph.
             - best_distance_m: Distance in meters between two found nodes.
    """
    # Extract valid nodes and its coordinates in radians
    ids1, coord_rad1 = _gather_coords(graph1, lat_key, lon_key)
    ids2, coord_rad2 = _gather_coords(graph2, lat_key, lon_key)

    # Check if both graphs have valid nodes. Otherwise, nothing to match
    if coord_rad1.shape[0] == 0 or coord_rad2.shape[0] == 0:
        raise ValueError("No geocoded nodes found in one of the graphs.")

    # Build a BallTree from a first graph
    tree = BallTree(coord_rad1, metric="haversine")

    # Query the nearest neighbor in graph1 for every node in graph2(only one)
    #    dists_rad: angular distance in radians
    #    idxs: indices of nearest neighbors in ids1
    dists_rad, idxs = tree.query(coord_rad2, k=1)

    # Find which query (node in graph2) has the smallest distance overall
    best_graph2 = int(np.argmin(dists_rad))
    best_graph1 = int(idxs[best_graph2, 0])

    # Convert angular distance(radians) → meters
    best_dist_m = float(dists_rad[best_graph2, 0]) * EARTH_RADIUS_M

    return ids1[best_graph1], ids2[best_graph2], best_dist_m
