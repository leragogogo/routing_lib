from graph.loader_osm import load_graph_from_osm_xml
from graph.visualizer import plot_graph
from algorithms.closest_pair import closest_pair

if __name__ == "__main__":
    graph_moabit = load_graph_from_osm_xml("data/moabit.osm", filter_name="driveable", strategy="largest")
    graph_wedding = load_graph_from_osm_xml("data/wedding.osm", filter_name="driveable", strategy="largest")
    graph_gesundbrunnen = load_graph_from_osm_xml("data/gesundbrunnen.osm", filter_name="driveable", strategy="largest")
    plot_graph(graph_moabit)
    print(closest_pair(graph_moabit, graph_gesundbrunnen))



