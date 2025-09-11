import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import pytest
from graph.loader_osm import load_graph_from_osm_xml


# Sample test data
@pytest.fixture
def sample_osm_xml_data():
    return """
    <osm version="0.6" generator="test">
        <node id="A" lat="52.52" lon="13.405" />
        <node id="B" lat="52.50" lon="13.39" />
        <way id="1">
            <nd ref="A" />
            <nd ref="B" />
        </way>
    </osm>
    """


# Monkeypatch built-in open to return a fake file object
@pytest.fixture
def mock_open(monkeypatch, sample_osm_xml_data):
    file_obj = io.StringIO(sample_osm_xml_data)

    def _mock_open(*args, **kwargs):
        file_obj.seek(0)
        return file_obj

    monkeypatch.setattr("builtins.open", _mock_open)


# Test using the mocked open and sample data
def test_load_graph_from_osm_xml(mock_open):
    graph = load_graph_from_osm_xml("fake_map.osm", directed=True)

    # Check nodes exist
    assert graph.has_node("A")
    assert graph.has_node("B")

    # Check attributes (lat/lon)
    attrs = graph.get_node("A").get_attrs()
    assert "lat" in attrs and "lon" in attrs

    # Check edge exist
    print(graph.get_neighbors("A"))
    print({"B": pytest.approx(graph.get_edge_cost("A", "B"))})
    assert graph.get_neighbors("A") == {"B": pytest.approx(graph.get_edge_cost("A", "B"))}


def test_osm_graph_with_no_nodes(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <way id="1">
            <nd ref="A" />
            <nd ref="B" />
        </way>
    </osm>
    """
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))
    graph = load_graph_from_osm_xml("fake.osm")

    # Should not crash, but nodes will not have lat/lon
    assert graph.has_node("A")
    assert graph.has_node("B")


def test_osm_graph_with_no_ways(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="A" lat="52.52" lon="13.405" />
        <node id="B" lat="52.50" lon="13.39" />
    </osm>
    """
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))
    graph = load_graph_from_osm_xml("fake.osm")

    assert not graph.has_node("A")
    assert not graph.has_node("B")


def test_empty_osm_file(monkeypatch):
    empty_osm = "<osm version='0.6'></osm>"
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(empty_osm))

    graph = load_graph_from_osm_xml("empty.osm")
    assert graph.get_all_nodes() == []


def test_undirected_osm_graph(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="X" lat="52.0" lon="13.0" />
        <node id="Y" lat="52.01" lon="13.01" />
        <way id="1">
            <nd ref="X" />
            <nd ref="Y" />
        </way>
    </osm>
    """
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))
    graph = load_graph_from_osm_xml("map.osm", directed=False)

    assert graph.get_edge_cost("X", "Y") > 0
    assert graph.get_edge_cost("Y", "X") > 0


# Test that additional attributes and <tag> children are parsed into node attrs.
def test_node_with_extra_attributes_and_tags(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="N1" lat="52.1" lon="13.1" user="bob" uid="1001">
            <tag k="amenity" v="cafe" />
            <tag k="name" v="Starbucks" />
        </node>
        <node id="N2" lat="52.8" lon="13.5" user="bob" uid="1002">
            <tag k="amenity" v="cafe" />
            <tag k="name" v="KFC" />
        </node>
        <way id="1">
            <nd ref="N1" />
            <nd ref="N2" />
        </way>
    </osm>
    """
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))

    graph = load_graph_from_osm_xml("tags.osm")
    assert graph.has_node("N1")

    attrs = graph.get_node("N1").get_attrs()

    assert attrs["lat"] == 52.1
    assert attrs["lon"] == 13.1
    assert attrs["user"] == "bob"
    assert attrs["uid"] == "1001"
    assert attrs["amenity"] == "cafe"
    assert attrs["name"] == "Starbucks"


def test_filter_name_driveable(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="A" lat="52.5" lon="13.4" />
        <node id="B" lat="52.6" lon="13.5" />
        <way id="1">
            <nd ref="A" />
            <nd ref="B" />
            <tag k="highway" v="residential" />
        </way>
        <way id="2">
            <nd ref="A" />
            <nd ref="B" />
            <tag k="highway" v="footway" />
        </way>
    </osm>
    """

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))
    graph = load_graph_from_osm_xml("map.osm", filter_name="driveable")

    # Only residential should be included
    assert graph.get_edge_cost("A", "B") > 0  # Way 1 only


def test_filter_name_pedestrian(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="X" lat="52.0" lon="13.0" />
        <node id="Y" lat="52.1" lon="13.1" />
        <way id="1">
            <nd ref="X" />
            <nd ref="Y" />
            <tag k="highway" v="footway" />
        </way>
        <way id="2">
            <nd ref="X" />
            <nd ref="Y" />
            <tag k="highway" v="motorway" />
        </way>
    </osm>
    """

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))
    graph = load_graph_from_osm_xml("ped.osm", filter_name="pedestrian")

    assert graph.get_edge_cost("X", "Y") > 0  # Way 1 only


def test_filter_name_bicycle(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="X" lat="52.0" lon="13.0" />
        <node id="Y" lat="52.1" lon="13.1" />
        <way id="1">
            <nd ref="X" />
            <nd ref="Y" />
            <tag k="highway" v="path" />
        </way>
        <way id="2">
            <nd ref="X" />
            <nd ref="Y" />
            <tag k="highway" v="motorway" />
        </way>
    </osm>
    """

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))
    graph = load_graph_from_osm_xml("ped.osm", filter_name="bicycle")

    assert graph.get_edge_cost("X", "Y") > 0  # Way 1 only


def test_custom_way_filter(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="M" lat="52.0" lon="13.0" />
        <node id="N" lat="52.01" lon="13.01" />
        <way id="1">
            <nd ref="M" />
            <nd ref="N" />
            <tag k="highway" v="primary" />
        </way>
        <way id="2">
            <nd ref="M" />
            <nd ref="N" />
            <tag k="highway" v="residential" />
        </way>
    </osm>
    """

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))

    def only_primary(tags: dict) -> bool:
        return tags.get("highway") == "primary"

    graph = load_graph_from_osm_xml("custom.osm", way_filter=only_primary)

    assert graph.get_edge_cost("M", "N") > 0  # Way 1 only


def test_way_filter_overrides_filter_name(monkeypatch):
    osm_data = """
    <osm version="0.6">
        <node id="C" lat="52.0" lon="13.0" />
        <node id="D" lat="52.1" lon="13.1" />
        <way id="1">
            <nd ref="C" />
            <nd ref="D" />
            <tag k="highway" v="cycleway" />
        </way>
    </osm>
    """

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))

    # Even though "driveable" would reject "cycleway",
    # the custom way_filter will accept all
    graph = load_graph_from_osm_xml(
        "override.osm",
        filter_name="driveable",
        way_filter=lambda tags: True  # Accept all ways
    )

    assert graph.get_edge_cost("C", "D") > 0


def test_invalid_filter_name_raises(monkeypatch):
    osm_data = "<osm version='0.6'></osm>"
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: io.StringIO(osm_data))

    with pytest.raises(ValueError):
        load_graph_from_osm_xml("invalid.osm", filter_name="spaceships")
