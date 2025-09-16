import folium
from graph.core import Graph


def plot_graph(graph: Graph, output_file: str = "graph_map.html", zoom_start: int = 15) -> None:
    """
    Visualize a graph using Folium (interactive web map).

    :param graph: Graph object with lat/lon in node attrs.
    :param output_file: File to save the HTML map to.
    :param zoom_start: Initial zoom level for the map.
    """
    # Get first node to center map
    first_node = next(iter(graph.get_all_nodes()), None)
    if not first_node:
        print("Graph is empty — nothing to plot.")
        return

    lat = first_node.get_attrs().get("lat",)
    lon = first_node.get_attrs().get("lon",)
    fmap = folium.Map(location=[lat, lon], zoom_start=zoom_start)

    # Add nodes
    for node in graph.get_all_nodes():
        attrs = node.get_attrs()
        lat, lon = attrs.get("lat"), attrs.get("lon")
        if lat is None or lon is None:
            continue
        folium.CircleMarker(
            location=(lat, lon),
            radius=2,
            color="red",
            fill=True,
            fill_opacity=0.8,
            popup=node.get_id()
        ).add_to(fmap)

    # Add edges
    for from_id in graph.nodes:
        from_node = graph.get_node(from_id)
        lat1, lon1 = from_node.get_attrs().get("lat"), from_node.get_attrs().get("lon")

        for to_id, _ in graph.get_neighbours(from_id).items():
            to_node = graph.get_node(to_id)
            lat2, lon2 = to_node.get_attrs().get("lat"), to_node.get_attrs().get("lon")

            if None not in (lat1, lon1, lat2, lon2):
                folium.PolyLine([(lat1, lon1), (lat2, lon2)], color="gray").add_to(fmap)

    # Save and notify
    fmap.save(output_file)
    print(f"✅ Map saved to {output_file}. Open it in your browser.")
