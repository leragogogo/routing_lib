import math
import numpy as np
import pytest

from graph.core import Graph
from algorithms.dijkstra import dijkstra, reconstruct_path
from algorithms.distance_matrix import distance_matrix


# ---------- helpers ----------

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


def test_distance_matrix_shapes_and_indices():
    g = build_undirected_triangle()
    stops = ["A", "B", "C"]
    M, idx, paths = distance_matrix(g, stops)

    assert isinstance(M, np.ndarray)
    assert M.shape == (3, 3)
    assert set(idx.keys()) == set(stops)
    assert all(idx[s] in (0, 1, 2) for s in stops)
    # index order must correspond to stops order
    assert [stops[i] for i in range(len(stops))] == [
        sorted(idx, key=lambda k: idx[k])[i] for i in range(len(stops))
    ]


def test_distance_values_match_dijkstra():
    g = build_undirected_triangle()
    stops = ["A", "B", "C"]
    M, idx, _ = distance_matrix(g, stops)

    # Distances from A via standalone Dijkstra
    dist, _ = dijkstra(g, "A")
    assert M[idx["A"], idx["A"]] == 0.0
    assert M[idx["A"], idx["B"]] == dist["B"] == 5.0
    assert M[idx["A"], idx["C"]] == dist["C"] == 7.0


def test_paths_reconstruction_present_and_correct():
    g = build_undirected_triangle()
    stops = ["A", "B", "C"]
    _, idx, paths = distance_matrix(g, stops)

    assert paths[("A", "B")] == ["A", "B"]
    assert paths[("A", "C")] == ["A", "B", "C"]
    assert paths[("B", "C")] == ["B", "C"]


def test_unreachable_pairs_are_inf_and_empty_path():
    g = build_with_unreachable()
    stops = ["A", "B", "D"]
    M, idx, paths = distance_matrix(g, stops)

    # D is isolated
    assert math.isinf(M[idx["A"], idx["D"]])
    assert math.isinf(M[idx["B"], idx["D"]])
    assert math.isinf(M[idx["D"], idx["A"]])
    assert paths[("A", "D")] == []
    assert paths[("B", "D")] == []
    assert paths[("D", "A")] == []


def test_diagonal_is_zero():
    g = build_undirected_triangle()
    stops = ["A", "B", "C"]
    M, idx, _ = distance_matrix(g, stops)
    for s in stops:
        assert M[idx[s], idx[s]] == 0.0


def test_symmetry_for_undirected_graph():
    g = build_undirected_triangle()
    stops = ["A", "B", "C"]
    M, idx, _ = distance_matrix(g, stops)

    for i in range(len(stops)):
        for j in range(len(stops)):
            assert M[i, j] == M[j, i]


def test_asymmetry_for_directed_graph():
    g = build_directed_asymmetric()
    stops = ["A", "B", "C"]
    M, idx, _ = distance_matrix(g, stops)

    # A->B cheap, B->A expensive
    assert M[idx["A"], idx["B"]] == 1.0
    assert M[idx["B"], idx["A"]] == 10.0
    # A->C uses A->B->C
    assert M[idx["A"], idx["C"]] == 2.0


def test_paths_align_with_matrix_entries():
    g = build_directed_asymmetric()
    stops = ["A", "B", "C"]
    M, idx, paths = distance_matrix(g, stops)

    # A->C should be via B with distance 2.0
    assert paths[("A", "C")] == ["A", "B", "C"]
    assert M[idx["A"], idx["C"]] == 2.0


def test_handles_single_stop():
    g = Graph(directed=False)
    g.add_node("X")
    stops = ["X"]
    M, idx, paths = distance_matrix(g, stops)

    assert M.shape == (1, 1)
    assert M[0, 0] == 0.0
    assert idx == {"X": 0}
    # no off-diagonal paths; diagonal path optional (your impl returns none for equal source/target)
    # So we just ensure there is no unexpected key:
    assert ("X", "X") not in paths or paths[("X", "X")] == ["X"]


def test_order_in_stops_reflects_rows_and_cols():
    g = build_undirected_triangle()
    # Non-sorted order on purpose
    stops = ["C", "A", "B"]
    M, idx, _ = distance_matrix(g, stops)

    # Row 0 is "C"
    assert idx["C"] == 0
    # Check a known distance aligns with this indexing
    # From "C" to "A" should be 7.0
    assert M[idx["C"], idx["A"]] == 7.0
