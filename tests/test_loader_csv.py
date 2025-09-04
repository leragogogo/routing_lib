import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import pytest
from graph.loader_csv import load_graph_from_csv


# Sample test data
@pytest.fixture
def sample_csv_data():
    return {
        "nodes": """id,lat,lon
A,52.52,13.405
B,52.50,13.39
""",
        "edges": """from,to,cost
A,B,2.3
B,A,2.5
"""
    }


# Monkeypatch built-in open to return a fake file object
@pytest.fixture
def mock_open(monkeypatch, sample_csv_data):
    def _mock_open(filepath, *args, **kwargs):
        if "nodes.csv" in filepath:
            return io.StringIO(sample_csv_data["nodes"])
        elif "edges.csv" in filepath:
            return io.StringIO(sample_csv_data["edges"])
        raise FileNotFoundError(f"Mocked open can't find: {filepath}")

    monkeypatch.setattr("builtins.open", _mock_open)


# Test using the mocked open and sample data
def test_load_graph_from_csv(mock_open):
    graph = load_graph_from_csv("nodes.csv", "edges.csv", directed=True)

    # Node checks
    assert graph.has_node("A")
    assert graph.has_node("B")
    assert graph.get_node("A").get_attrs()["lat"] == 52.52

    # Edge checks
    assert graph.get_neighbors("A") == {"B": 2.3}
    assert graph.get_neighbors("B") == {"A": 2.5}
    assert graph.get_edge_cost("A", "B") == 2.3
    assert graph.get_edge_cost("B", "A") == 2.5


def test_load_graph_with_no_nodes(monkeypatch):
    edges_csv = """from,to,cost
A,B,1.0
"""
    nodes_csv = ""  # No nodes declared

    def _mock_open(filepath, *args, **kwargs):
        if "nodes.csv" in filepath:
            return io.StringIO(nodes_csv)
        elif "edges.csv" in filepath:
            return io.StringIO(edges_csv)
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", _mock_open)

    graph = load_graph_from_csv("nodes.csv", "edges.csv")
    assert graph.has_node("A")
    assert graph.has_node("B")
    assert graph.get_edge_cost("A", "B") == 1.0


def test_load_graph_with_no_edges(monkeypatch):
    nodes_csv = """id
A
B
"""
    edges_csv = ""  # No edges

    def _mock_open(filepath, *args, **kwargs):
        if "nodes.csv" in filepath:
            return io.StringIO(nodes_csv)
        elif "edges.csv" in filepath:
            return io.StringIO(edges_csv)
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", _mock_open)

    graph = load_graph_from_csv("nodes.csv", "edges.csv")
    assert graph.has_node("A")
    assert graph.has_node("B")
    assert graph.get_neighbors("A") == {}


def test_load_empty_csv(monkeypatch):
    nodes_csv = ""
    edges_csv = ""

    def _mock_open(filepath, *args, **kwargs):
        if "nodes.csv" in filepath:
            return io.StringIO(nodes_csv)
        elif "edges.csv" in filepath:
            return io.StringIO(edges_csv)
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", _mock_open)

    graph = load_graph_from_csv("nodes.csv", "edges.csv")
    assert graph.get_all_nodes() == []


def test_undirected_graph(monkeypatch):
    nodes_csv = """id
X
Y
"""
    edges_csv = """from,to,cost
X,Y,10
"""

    def _mock_open(filepath, *args, **kwargs):
        if "nodes.csv" in filepath:
            return io.StringIO(nodes_csv)
        elif "edges.csv" in filepath:
            return io.StringIO(edges_csv)
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", _mock_open)

    graph = load_graph_from_csv("nodes.csv", "edges.csv", directed=False)
    assert graph.get_edge_cost("X", "Y") == 10
    assert graph.get_edge_cost("Y", "X") == 10  # reverse edge


def test_node_with_attributes(monkeypatch):
    nodes_csv = """id,lat,name
N1,10.5,Start
"""
    edges_csv = ""

    def _mock_open(filepath, *args, **kwargs):
        if "nodes.csv" in filepath:
            return io.StringIO(nodes_csv)
        elif "edges.csv" in filepath:
            return io.StringIO(edges_csv)
        raise FileNotFoundError

    monkeypatch.setattr("builtins.open", _mock_open)

    graph = load_graph_from_csv("nodes.csv", "edges.csv")
    node = graph.get_node("N1")

    assert node.get_attrs()["lat"] == 10.5
    assert node.get_attrs()["name"] == "Start"
