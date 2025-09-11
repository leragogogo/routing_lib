from graph.loader_osm import load_graph_from_osm_xml
from graph.visualizer import plot_graph

if __name__ == "__main__":
    graph = load_graph_from_osm_xml("data/sample.osm", filter_name="driveable", strategy="largest")
    plot_graph(graph)



