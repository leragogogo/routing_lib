from pathlib import Path
from .loader_csv import CSVLoader
from .loader_json import JSONLoader
from .loader_osm import OSMLoader
from .loader import CSVSource, JSONSource, OSMSource, LoadOptions
from graph.core import Graph

_REGISTRY = {
    CSVSource: CSVLoader,
    JSONSource: JSONLoader,
    OSMSource: OSMLoader,
}


def load_graph(source: any, options: LoadOptions) -> Graph:
    """
    Load a graph using the appropriate loader, selected by the type of source.

    The factory looks up the loader class from the internal registry,
    which maps each supported source type (e.g., `CSVSource`, `JSONSource`, `OSMSource`)
    to its corresponding loader implementation (`CSVLoader`, `JSONLoader`, `OSMLoader`).
    It then delegates the actual parsing and graph construction to that loader.

    :param source: A source object describing where and how to load the graph data.
            Supported types include:
              - CSVSource (with node and edge file paths).
              - JSONSource (with a single JSON file path).
              - OSMSource (with OSM XML file path and optional filters).
    :param options: LoadOptions:
            Options controlling how the graph is built, including:
              - directed (bool): whether to create a directed graph.
              - strategy (str): component handling strategy.
                "all": keep all components.
                "largest": keep only the largest connected component.
                "label": keep all components, adding a `component_id` attribute.

    :return: Graph object
    """
    cls = _REGISTRY.get(type(source))
    if not cls:
        raise ValueError(f'Not supported type of source: ${type(source).__name__}')
    return cls().load(source, options)
