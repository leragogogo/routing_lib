import folium
from folium.features import DivIcon
from graph.core import Graph


class GraphVisualizer:
    """
    Visualizer of a graph on the map
    """
    def __init__(
            self,
            zoom_start: int = 14,
            tiles: str = "OpenStreetMap"
    ):
        self._map = folium.Map([0, 0], zoom_start=zoom_start, tiles=tiles)

    def _update_map_center(self, graph: Graph) -> None:
        """
        Center map to a first node found in graph.

        :param graph: Graph objects
        """
        # Get first node to center map
        first_node = next(iter(graph.get_all_nodes()), None)
        if not first_node:
            print("Graph is empty. Nothing to plot.")
            return

        # Update the map center
        lat = first_node.get_attrs().get("lat")
        lon = first_node.get_attrs().get("lon")
        self._map.location = [lat, lon]

    def add_graph(self, graph: Graph) -> None:
        """
        Visualize a graph on the map.

        :param graph: Graph object
        :return:
        """
        self._update_map_center(graph)

        # Add nodes to the map
        for node in graph.get_all_nodes():
            attrs = node.get_attrs()
            lat, lon = attrs.get("lat"), attrs.get("lon")
            if lat is None or lon is None:
                continue

            folium.CircleMarker(
                location=(lat, lon),
                radius=2,
                color="black",
                fill=True,
                fill_opacity=0.8,
                popup=node.get_id()
            ).add_to(self._map)

        # Add edges to the map
        for from_id in graph.nodes:
            from_node = graph.get_node(from_id)
            lat1, lon1 = from_node.get_attrs().get("lat"), from_node.get_attrs().get("lon")

            for to_id, _ in graph.get_neighbours(from_id).items():
                to_node = graph.get_node(to_id)
                lat2, lon2 = to_node.get_attrs().get("lat"), to_node.get_attrs().get("lon")

                if None not in (lat1, lon1, lat2, lon2):
                    folium.PolyLine([(lat1, lon1), (lat2, lon2)], color="gray").add_to(self._map)

    def add_tour(self, graph: Graph, tour_ids: list[str], paths: dict[tuple[str, str], list[str]],
                 optimal_distance: float) -> None:
        """
        Visualize tour found with TSP algorithms.

        :param graph: Graph object
        :param tour_ids: List of node ids that tour consists of
        :param paths: Paths between source and destination
        :param optimal_distance:
        """
        self._update_map_center(graph)

        # Create a feature group named with the distance
        fg = folium.FeatureGroup(name=f"TSP Tour — {optimal_distance:.2f} m", show=True)

        # Add nodes to the map
        for i, node_id in enumerate(tour_ids):
            node = graph.get_node(node_id)
            attrs = node.get_attrs()
            lat, lon = attrs.get("lat"), attrs.get("lon")
            if lat is None or lon is None:
                continue

            # The number label for order of visiting
            folium.Marker(
                location=(lat, lon),
                icon=DivIcon(
                    icon_size=(20, 20),
                    icon_anchor=(10, 10),
                    html=f"""
                            <div style="
                                background: rgba(255,255,255,0.85);
                                border: 1px solid #333;
                                border-radius: 10px;
                                padding: 1px 5px;
                                font-size: 11px;
                                line-height: 1;
                                text-align: center;">
                                {i}
                            </div>
                        """
                )
            ).add_to(fg)

        # Add edges to the map
        for i in range(1, len(tour_ids)):
            # Get the path from prev to current node
            path = paths[(tour_ids[i - 1], tour_ids[i])]
            for j in range(1, len(path)):
                from_node = graph.get_node(path[j - 1])
                lat1, lon1 = from_node.get_attrs().get("lat"), from_node.get_attrs().get("lon")

                to_node = graph.get_node(path[j])
                lat2, lon2 = to_node.get_attrs().get("lat"), to_node.get_attrs().get("lon")

                if None not in (lat1, lon1, lat2, lon2):
                    folium.PolyLine(
                        [(lat1, lon1), (lat2, lon2)],
                        color="red"
                    ).add_to(fg)

        # Add the feature group to the map
        fg.add_to(self._map)

        # Ensure a layer control exists (so user can toggle tours)
        folium.LayerControl(collapsed=False).add_to(self._map)

    def save_file(self, output_file: str = "graph_map.html") -> None:
        self._map.save(output_file)
        print(f"Map saved to {output_file}. Open it in your browser.")
