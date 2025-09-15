import numpy as np
import pytest

from algorithms.tsp_2opt import tsp_2opt


def test_open_path_no_crossing_remains_same():
    # A simple line A-B-C-D, already optimal
    stops = ["A", "B", "C", "D"]
    index = {s: i for i, s in enumerate(stops)}
    dist = np.array([
        [0, 1, 2, 3],
        [1, 0, 1, 2],
        [2, 1, 0, 1],
        [3, 2, 1, 0],
    ], float)

    tour = ["A", "B", "C", "D"]
    length = 3.0
    improved, improved_len = tsp_2opt(dist, index, tour, length)

    # Path is already optimal
    assert improved == tour
    assert improved_len == 3.0


def test_open_path_with_crossing_gets_fixed():
    stops = ["A", "B", "C", "D"]
    index = {s: i for i, s in enumerate(stops)}
    dist = np.array([
        [0, 1, 2, 9],  # A
        [1, 0, 9, 1],  # B
        [2, 9, 0, 1],  # C
        [9, 1, 1, 0],  # D
    ], float)

    tour = ["A", "C", "B", "D"]
    length = 12
    improved, improved_len = tsp_2opt(dist, index, tour, length)

    assert improved == ["A", "B", "C", "D"]
    assert improved_len < length


def test_cycle_no_crossing_remains_same():
    stops = ["A", "B", "C", "D"]
    index = {s: i for i, s in enumerate(stops)}
    dist = np.ones((4, 4))
    np.fill_diagonal(dist, 0)

    tour = ["A", "B", "C", "D", "A"]
    length = 4.0
    improved, improved_len = tsp_2opt(dist, index, tour, length)

    # Cycle must remain closed
    assert improved == ["A", "B", "C", "D", "A"]


def test_closed_cycle_with_crossing_gets_fixed():
    # Square: A-B-C-D-A but with a crossing order A-C-B-D-A
    stops = ["A", "B", "C", "D"]
    index = {s: i for i, s in enumerate(stops)}
    dist = np.array([
        [0, 1, 2, 1],  # A
        [1, 0, 1, 2],  # B
        [2, 1, 0, 1],  # C
        [1, 2, 1, 0],  # D
    ], float)

    tour = ["A", "C", "B", "D", "A"]
    length = 6
    improved, improved_len = tsp_2opt(dist, index, tour, length)

    assert improved == ["A", "B", "C", "D", "A"]
    assert improved_len <= 4.0


def test_short_tour_raises():
    dist = np.zeros((2, 2))
    index = {"A": 0, "B": 1}
    tour = ["A", "B"]
    with pytest.raises(ValueError):
        tsp_2opt(dist, index, tour, 0.0)
