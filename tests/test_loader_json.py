import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import io
import pytest
from graph.loader_json import load_graph_from_json


# Sample test data
@pytest.fixture
def sample_json_data():
    return {
        "nodes": [
            {"id": "A", "lat": 52.52, "lon": 13.405},
            {"id": "B", "lat": 52.50, "lon": 13.39}
        ],
        "edges": [
            {"from": "A", "to": "B", "cost": 2.3},
            {"from": "B", "to": "A", "cost": 2.5}
        ]
    }


# Monkeypatch built-in open to return a fake file object
@pytest.fixture
def mock_open(monkeypatch, sample_json_data):
    json_str = json.dumps(sample_json_data)
    file_obj = io.StringIO(json_str)

    def _mock_open(*args, **kwargs):
        file_obj.seek(0)
        return file_obj

    monkeypatch.setattr("builtins.open", _mock_open)


# Test using the mocked open and sample data
def test_load_graph_from_json(mock_open):
    graph = load_graph_from_json("fake_path.json", directed=True)

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
    json_data = {
        "edges": [{"from": "A", "to": "B", "cost": 1.0}]
    }
    json_str = json.dumps(json_data)
    fake_file = io.StringIO(json_str)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: fake_file)
    graph = load_graph_from_json("fake.json")

    # Should still create nodes from edges
    assert graph.has_node("A")
    assert graph.has_node("B")
    assert graph.get_edge_cost("A", "B") == 1.0


def test_load_graph_with_no_edges(monkeypatch):
    json_data = {
        "nodes": [{"id": "A"}, {"id": "B"}]
    }
    json_str = json.dumps(json_data)
    fake_file = io.StringIO(json_str)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: fake_file)
    graph = load_graph_from_json("fake.json")

    assert graph.has_node("A")
    assert graph.has_node("B")
    assert graph.get_neighbors("A") == {}


def test_load_empty_json(monkeypatch):
    json_data = {}
    json_str = json.dumps(json_data)
    fake_file = io.StringIO(json_str)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: fake_file)
    graph = load_graph_from_json("fake.json")

    assert graph.get_all_nodes() == []


def test_load_graph_missing_edge_cost(monkeypatch):
    json_data = {
        "nodes": [{"id": "A"}, {"id": "B"}],
        "edges": [{"from": "A", "to": "B"}]  # Missing "cost"
    }
    json_str = json.dumps(json_data)
    fake_file = io.StringIO(json_str)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: fake_file)

    with pytest.raises(KeyError):
        load_graph_from_json("fake.json")


def test_undirected_graph(monkeypatch):
    json_data = {
        "nodes": [{"id": "X"}, {"id": "Y"}],
        "edges": [{"from": "X", "to": "Y", "cost": 10}]
    }
    json_str = json.dumps(json_data)
    fake_file = io.StringIO(json_str)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: fake_file)
    graph = load_graph_from_json("fake.json", directed=False)

    assert graph.get_edge_cost("X", "Y") == 10
    assert graph.get_edge_cost("Y", "X") == 10  # reverse edge must exist


def test_node_with_attributes(monkeypatch):
    json_data = {
        "nodes": [{"id": "N1", "lat": 10.5, "name": "My Node"}],
        "edges": []
    }
    json_str = json.dumps(json_data)
    fake_file = io.StringIO(json_str)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: fake_file)
    graph = load_graph_from_json("fake.json")

    node = graph.get_node("N1")
    assert node.get_attrs()["lat"] == 10.5
    assert node.get_attrs()["name"] == "My Node"
