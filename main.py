from graph.loader.loader_factory import load_graph
from graph.core import Graph
from graph.visualizer import GraphVisualizer
from algorithms.closest_pair import closest_pair
from graph.loader.loader import CSVSource, JSONSource, OSMSource, LoadOptions
from algorithms.distance_matrix import distance_matrix
from algorithms.tsp_nn import tsp_nn
from algorithms.tsp_2opt import tsp_2opt
from algorithms.tsp_held_karp import tsp_held_karp
import random


def get_random_nodes(graph: Graph) -> list[str]:
    nodes = graph.get_all_nodes()
    nodes_ids = [node_id.get_id() for node_id in nodes]
    n = random.randint(3, 20)
    stops = []
    while len(stops) != n:
        choice = random.choice(nodes_ids)
        if choice not in stops:
            stops.append(choice)

    return stops


# Examples of usage
if __name__ == "__main__":
    # Load graph from JSON, add it to map,
    # and find the optimal(not guaranteed) tour using NN algorithm.
    graph_moabit_json = load_graph(
        JSONSource(
            "data/moabit.json"
        ),
        LoadOptions(
            strategy="largest"
        )
    )
    map_graph_moabit_json = GraphVisualizer()
    map_graph_moabit_json.add_graph(graph_moabit_json)
    random_stops = get_random_nodes(graph_moabit_json)
    distances, node_to_index, _, paths = distance_matrix(
        graph_moabit_json,
        random_stops
    )
    tours_id, total_len = tsp_nn(
        random_stops, distances,
        node_to_index, random_stops[0], True
    )
    map_graph_moabit_json.add_tour(graph_moabit_json, tours_id, paths, total_len)
    map_graph_moabit_json.save_file("moabit_graph_json_nn.html")

    # Load graph from CSV, add it to map,
    # and find the optimal(better than NN) tour using 2-opt optimization technique.
    graph_moabit_csv = load_graph(
        CSVSource(
            "data/moabit_nodes.csv",
            "data/moabit_edges.csv"
        ),
        LoadOptions(
            strategy="largest"
        )
    )
    map_graph_moabit_csv = GraphVisualizer()
    map_graph_moabit_csv.add_graph(graph_moabit_csv)
    distances, node_to_index, _, paths = distance_matrix(
        graph_moabit_csv,
        random_stops
    )
    tours_id, total_len = tsp_nn(
        random_stops, distances,
        node_to_index, random_stops[0], True
    )
    tours_id, total_len = tsp_2opt(
        distances, node_to_index,
        tours_id, total_len
    )
    map_graph_moabit_csv.add_tour(graph_moabit_csv, tours_id, paths, total_len)
    map_graph_moabit_csv.save_file("moabit_graph_csv_2opt.html")

    # Load graph from OSM, add it to map,
    # and find the optimal(guaranteed) tour using Held-Karp algorithm.
    graph_moabit_osm = load_graph(
        OSMSource("data/moabit.osm",),
        LoadOptions(strategy="largest")
    )
    map_graph_moabit_osm = GraphVisualizer()
    map_graph_moabit_osm.add_graph(graph_moabit_osm)
    distances, _, index_to_node, paths = distance_matrix(
        graph_moabit_osm,
        random_stops
    )
    tours_id, total_len = tsp_held_karp(
        distances,
        index_to_node
    )
    map_graph_moabit_osm.add_tour(graph_moabit_osm, tours_id, paths, total_len)
    map_graph_moabit_osm.save_file("moabit_graph_osm_held_karp.html")

    # Find the closest nodes from each graph.
    graph_gesundbrunnen_osm = load_graph(
        OSMSource("data/gesundbrunnen.osm", filter_name="driveable"),
        LoadOptions(strategy="largest")
    )
    print(closest_pair(graph_moabit_osm, graph_gesundbrunnen_osm))
