import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.core import Graph
from graph.utils import connected_components, extract_component, apply_component_strategy


def build_test_graph():
    """
    Build a graph with 2 connected components:
    Component 1: A-B-C
    Component 2: D-E
    """
    g = Graph(directed=False)

    # Component 1
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_edge("A", "B", cost=1)
    g.add_edge("B", "C", cost=1)

    # Component 2
    g.add_node("D")
    g.add_node("E")
    g.add_edge("D", "E", cost=1)

    return g


def test_connected_components_finds_all():
    g = build_test_graph()
    comps = connected_components(g)

    # Expect 2 components
    assert len(comps) == 2

    # Each is a set of nodes
    all_nodes = set().union(*comps)
    assert all_nodes == {"A", "B", "C", "D", "E"}

    # Components should be disjoint
    assert comps[0].isdisjoint(comps[1])


def test_extract_component_returns_subgraph():
    g = build_test_graph()
    comps = connected_components(g)
    first_comp = comps[0]

    subgraph = extract_component(g, first_comp)

    # Subgraph contains only nodes from that component
    assert set(subgraph.nodes.keys()) == first_comp

    # All edges should connect only nodes inside that component
    for n in subgraph.nodes:
        for neigh in subgraph.get_node(n).neighbours:
            assert neigh in first_comp


def test_strategy_all_keeps_graph():
    g = build_test_graph()
    g2 = apply_component_strategy(g, strategy="all")
    assert g2 is g  # should return same object


def test_strategy_largest_returns_only_biggest_component():
    g = build_test_graph()
    g2 = apply_component_strategy(g, strategy="largest")

    # Largest component has 3 nodes
    assert set(g2.nodes.keys()) == {"A", "B", "C"}


def test_strategy_label_adds_component_id():
    g = build_test_graph()
    g2 = apply_component_strategy(g, strategy="label")

    # All nodes should now have a component_id attribute
    comp_ids = {g2.get_node(n).attrs["component_id"] for n in g2.nodes}
    assert comp_ids == {0, 1}  # two components, ids 0 and 1

    # Nodes from same component must share the same id
    comps = connected_components(g)
    for cid, comp in enumerate(comps):
        for n in comp:
            assert g2.get_node(n).attrs["component_id"] == cid


def test_strategy_invalid_raises():
    g = build_test_graph()
    with pytest.raises(ValueError):
        apply_component_strategy(g, strategy="foobar")
