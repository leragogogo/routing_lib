from graph.loader.loader_factory import load_graph
from graph.visualizer import plot_graph
from algorithms.closest_pair import closest_pair
from graph.loader.loader import CSVSource, JSONSource, OSMSource, LoadOptions

if __name__ == "__main__":
    graph_moabit = load_graph(
        OSMSource("data/moabit.osm", filter_name="driveable"),
        LoadOptions(strategy="largest")
    )
    plot_graph(graph_moabit)
    # print(closest_pair(graph_moabit, graph_gesundbrunnen))
