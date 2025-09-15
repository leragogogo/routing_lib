import math
import pytest

from graph.core import Graph
from algorithms.dijkstra import dijkstra, reconstruct_path


def build_undirected_triangle():
    g = Graph(directed=False)
    for n in ["A", "B", "C"]:
        g.add_node(n)
    g.add_edge("A", "B", 5)
    g.add_edge("B", "C", 2)
    g.add_edge("A", "C", 9)
    return g


def build_with_unreachable():
    g = build_undirected_triangle()
    g.add_node("D")  # isolated
    return g


def build_directed_asymmetric():
    g = Graph(directed=True)
    for n in ["A", "B", "C"]:
        g.add_node(n)
    g.add_edge("A", "B", 1)
    g.add_edge("B", "A", 10)
    g.add_edge("B", "C", 1)
    return g


def build_line():
    g = Graph(directed=False)
    for n in ["A", "B", "C", "D"]:
        g.add_node(n)
    g.add_edge("A", "B", 1)
    g.add_edge("B", "C", 1)
    g.add_edge("C", "D", 1)
    return g


def test_dijkstra_distances_undirected_triangle():
    g = build_undirected_triangle()
    dist, prev = dijkstra(g, source="A")
    assert dist["A"] == 0.0
    assert dist["B"] == 5.0
    assert dist["C"] == 7.0  # A->B->C
    assert reconstruct_path(prev, "A", "C") == ["A", "B", "C"]


def test_reconstruct_path_returns_empty_when_unreachable():
    g = build_with_unreachable()
    dist, prev = dijkstra(g, source="A")
    assert math.isinf(dist["D"])
    assert reconstruct_path(prev, "A", "D") == []


def test_dijkstra_directed_asymmetry():
    g = build_directed_asymmetric()
    # From A
    dist_a, prev_a = dijkstra(g, source="A")
    assert dist_a["A"] == 0.0
    assert dist_a["B"] == 1.0
    assert dist_a["C"] == 2.0
    assert reconstruct_path(prev_a, "A", "C") == ["A", "B", "C"]

    # From B to A uses the expensive reverse arc
    dist_b, prev_b = dijkstra(g, source="B")
    assert dist_b["A"] == 10.0
    assert reconstruct_path(prev_b, "B", "A") == ["B", "A"]


def test_dijkstra_early_exit_stops_at_target():
    g = build_line()  # A-B-C-D with cost 1 each
    dist, prev = dijkstra(g, source="A", target="C")

    # Should find correct distance/path to C
    assert dist["C"] == 2.0
    assert reconstruct_path(prev, "A", "C") == ["A", "B", "C"]

    # And nodes beyond target are allowed to remain at inf (early exit)
    assert math.isinf(dist["D"])


def test_dijkstra_handles_stale_heap_entries():
    g = Graph(directed=True)
    for n in ["A", "B", "C"]:
        g.add_node(n)
    g.add_edge("A", "B", 5)
    g.add_edge("A", "C", 2)
    g.add_edge("C", "B", 1)

    dist, prev = dijkstra(g, source="A")
    assert dist["B"] == 3.0
    assert reconstruct_path(prev, "A", "B") == ["A", "C", "B"]
