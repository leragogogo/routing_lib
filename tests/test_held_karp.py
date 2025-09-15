import numpy as np
import pytest

from algorithms.tsp_held_karp import tsp_held_karp


def assert_valid_cycle(tour_ids, start_id, expected_nodes):
    # starts/ends at start_id and visits all expected nodes exactly once (in between)
    assert tour_ids[0] == start_id and tour_ids[-1] == start_id
    inner = tour_ids[1:-1]
    assert set(inner) == set(expected_nodes) - {start_id}
    assert len(inner) == len(expected_nodes) - 1
    # all unique inside (no repeats)
    assert len(inner) == len(set(inner))


def test_two_nodes_directed_cycle():
    # 0 -> 1 -> 0
    dist = np.array([
        [0, 3],
        [2, 0],
    ], dtype=float)
    index_to_node = {0: "A", 1: "B"}
    node_to_index = {v: k for k, v in index_to_node.items()}

    tour_ids, cost = tsp_held_karp(dist, index_to_node)

    assert_valid_cycle(tour_ids, "A", {"A", "B"})
    # Only possible cycle cost: A->B (3) + B->A (2) = 5
    assert cost == 5.0


def test_four_nodes_symmetric_known_optimum():
    # Example from the explanation; optimal cost = 21
    # One optimal tour is 0->2->3->1->0
    dist = np.array([
        [0, 2, 9, 10],
        [1, 0, 6, 4],
        [15, 7, 0, 8],
        [6, 3, 12, 0],
    ], dtype=float)

    index_to_node = {0: "A", 1: "B", 2: "C", 3: "D"}
    node_to_index = {v: k for k, v in index_to_node.items()}

    tour_ids, cost = tsp_held_karp(dist, index_to_node)

    assert_valid_cycle(tour_ids, "A", {"A", "B", "C", "D"})
    assert cost == 21.0


def test_five_nodes_symmetric_known_optimum():
    # Classic 5-node example; optimal cost = 26 (e.g., 0-1-3-2-4-0)
    dist = np.array([
        [0, 2, 9, 10, 7],
        [2, 0, 6, 4, 3],
        [9, 6, 0, 8, 5],
        [10, 4, 8, 0, 6],
        [7, 3, 5, 6, 0],
    ], dtype=float)

    index_to_node = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}
    node_to_index = {v: k for k, v in index_to_node.items()}

    tour_ids, cost = tsp_held_karp(dist, index_to_node)

    assert_valid_cycle(tour_ids, "A", {"A", "B", "C", "D", "E"})
    assert cost == 26.0


def test_four_nodes_asymmetric_directed():
    # Directed costs; best cycle is 0->1->2->3->0 with cost 1+1+1+1 = 4
    dist = np.array([
        [0, 1, 5, 5],
        [2, 0, 1, 5],
        [5, 2, 0, 1],
        [1, 5, 2, 0],
    ], dtype=float)

    index_to_node = {0: "S", 1: "X", 2: "Y", 3: "Z"}

    tour_ids, cost = tsp_held_karp(dist, index_to_node)

    assert_valid_cycle(tour_ids, "S", {"S", "X", "Y", "Z"})
    assert cost == 4.0


def test_mapping_is_used_not_identity():
    # Ensure function returns IDs from index_to_node mapping (not raw indices)
    dist = np.array([
        [0, 2, 3],
        [2, 0, 1],
        [3, 1, 0],
    ], dtype=float)
    # Non-trivial mapping
    index_to_node = {0: "X0", 1: "Y1", 2: "Z2"}
    node_to_index = {v: k for k, v in index_to_node.items()}

    tour_ids, cost = tsp_held_karp(dist, index_to_node)

    # Should start/end at "X0"
    assert tour_ids[0] == tour_ids[-1] == "X0"
    # Returned labels should be strings from mapping, not integers
    assert all(isinstance(x, str) for x in tour_ids)
