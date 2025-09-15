import numpy as np
import pytest

from algorithms.tsp_nn import tsp_nn


def make_index(stops):
    return {s: i for i, s in enumerate(stops)}


def test_nn_open_tour_simple_chain():
    # A -> B -> C -> D (unit costs). NN should pick a straight chain.
    stops = ["A", "B", "C", "D"]
    M = np.array([
        [0, 1, 5, 5],
        [1, 0, 1, 5],
        [5, 1, 0, 1],
        [5, 5, 1, 0],
    ], dtype=float)
    idx = make_index(stops)

    tour, length = tsp_nn(stops, M, idx, start="A", return_to_start=False)

    assert tour == ["A", "B", "C", "D"]
    assert length == 3.0


def test_nn_closed_tour_square_breaks_ties_by_costs():
    # Force a clear NN path around a square: A->B->C->D->A
    stops = ["A", "B", "C", "D"]
    M = np.array([
        [0, 1, 9, 2],   # A -> B (1) preferred over A -> D(2)
        [1, 0, 1, 9],
        [9, 1, 0, 1],
        [2, 9, 1, 0],   # D -> A (2) close the tour
    ], dtype=float)
    idx = make_index(stops)

    tour, length = tsp_nn(stops, M, idx, start="A", return_to_start=True)

    assert tour == ["A", "B", "C", "D", "A"]
    assert length == 5.0


def test_nn_asymmetric_directed_matrix_open():
    # Directed/asymmetric: A->B=1, B->C=1, A->C=5; NN: A->B->C
    stops = ["A", "B", "C"]
    inf = np.inf
    M = np.array([
        [0, 1, 5],
        [10, 0, 1],
        [10, 10, 0],
    ], dtype=float)
    idx = make_index(stops)

    tour, length = tsp_nn(stops, M, idx, start="A", return_to_start=False)

    assert tour == ["A", "B", "C"]
    assert length == 2.0


def test_nn_raises_on_shape_mismatch():
    stops = ["A", "B", "C"]
    M = np.zeros((2, 2), dtype=float)  # wrong shape
    idx = make_index(stops)

    with pytest.raises(ValueError):
        tsp_nn(stops, M, idx, start="A")


def test_nn_raises_on_missing_start():
    stops = ["A", "B"]
    M = np.array([[0, 1], [1, 0]], dtype=float)
    idx = make_index(stops)

    with pytest.raises(ValueError):
        tsp_nn(stops, M, idx, start="Z")


def test_nn_raises_on_disconnected_midway():
    # A -> B ok, but from B no unvisited node is reachable
    stops = ["A", "B", "C"]
    inf = np.inf
    M = np.array([
        [0, 1, inf],   # from A we can reach B only
        [inf, 0, inf], # from B no way to go to C
        [inf, inf, 0],
    ], dtype=float)
    idx = make_index(stops)

    with pytest.raises(ValueError) as e:
        tsp_nn(stops, M, idx, start="A", return_to_start=False)
    assert "No reachable next stop" in str(e.value)


def test_nn_raises_if_cannot_return_to_start():
    # Open path A->B->C works, but returning C->A is unreachable
    stops = ["A", "B", "C"]
    inf = np.inf
    M = np.array([
        [0, 1, inf],
        [1, 0, 1],
        [inf, 1, 0],
    ], dtype=float)
    idx = make_index(stops)

    with pytest.raises(ValueError) as e:
        tsp_nn(stops, M, idx, start="A", return_to_start=True)
    assert "Cannot return to start" in str(e.value)


def test_nn_visits_each_stop_once_no_revisits():
    # Matrix where revisiting would be tempting if visited mask wasn't used
    # NN should still produce a Hamiltonian path (unique nodes).
    stops = ["A", "B", "C", "D"]
    M = np.array([
        [0, 1, 2, 3],
        [1, 0, 1, 2],
        [2, 1, 0, 1],
        [3, 2, 1, 0],
    ], dtype=float)
    idx = make_index(stops)

    tour, length = tsp_nn(stops, M, idx, start="A", return_to_start=False)

    # All nodes are visited exactly once
    assert tour[0] == "A"
    assert len(tour) == len(set(tour)) == 4
    # Length should be finite
    assert np.isfinite(length)


def test_nn_single_stop_open_and_closed():
    stops = ["X"]
    M = np.array([[0.0]], dtype=float)
    idx = make_index(stops)

    # Open
    tour, length = tsp_nn(stops, M, idx, start="X", return_to_start=False)
    assert tour == ["X"]
    assert length == 0.0

    # Closed
    tour, length = tsp_nn(stops, M, idx, start="X", return_to_start=True)
    assert tour == ["X", "X"]
    assert length == 0.0
