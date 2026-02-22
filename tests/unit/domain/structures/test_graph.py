"""Unit tests for Graph."""
from __future__ import annotations

import pytest

from src.domain.structures import Graph
from src.domain.structures.exceptions import NodeNotFoundError


class TestGraphBasics:
    def test_empty_graph(self) -> None:
        g: Graph[str] = Graph()
        assert g.is_empty()
        assert g.size() == 0

    def test_add_node(self) -> None:
        g: Graph[str] = Graph()
        g.add_node("A")
        assert g.contains("A")
        assert g.size() == 1

    def test_add_node_idempotent(self) -> None:
        g: Graph[str] = Graph()
        g.add_node("A")
        g.add_node("A")
        assert g.size() == 1

    def test_iter_yields_nodes(self) -> None:
        g: Graph[str] = Graph()
        for n in ["A", "B", "C"]:
            g.add_node(n)
        assert set(g) == {"A", "B", "C"}

    def test_repr(self) -> None:
        g: Graph[str] = Graph()
        g.add_node("X")
        assert "Graph" in repr(g)


class TestGraphEdgesUndirected:
    def test_add_edge_creates_nodes(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        assert g.contains("A")
        assert g.contains("B")

    def test_undirected_bidirectional(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        assert "B" in g.neighbors("A")
        assert "A" in g.neighbors("B")

    def test_remove_edge(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        result = g.remove_edge("A", "B")
        assert result is True
        assert "B" not in g.neighbors("A")
        assert "A" not in g.neighbors("B")

    def test_remove_missing_edge_returns_false(self) -> None:
        g: Graph[str] = Graph()
        g.add_node("A")
        g.add_node("B")
        assert g.remove_edge("A", "B") is False


class TestGraphEdgesDirected:
    def test_directed_one_way(self) -> None:
        g: Graph[str] = Graph(directed=True)
        g.add_edge("A", "B")
        assert "B" in g.neighbors("A")
        assert "A" not in g.neighbors("B")

    def test_directed_remove_edge(self) -> None:
        g: Graph[str] = Graph(directed=True)
        g.add_edge("A", "B")
        g.remove_edge("A", "B")
        assert "B" not in g.neighbors("A")
        assert "A" not in g.neighbors("B")  # was never there


class TestGraphRemoveNode:
    def test_remove_node(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.remove_node("B")
        assert not g.contains("B")
        assert "B" not in g.neighbors("A")
        assert "B" not in g.neighbors("C")

    def test_remove_missing_node_returns_false(self) -> None:
        g: Graph[str] = Graph()
        assert g.remove_node("Z") is False


class TestGraphNeighbors:
    def test_neighbors_unknown_node_raises(self) -> None:
        g: Graph[str] = Graph()
        with pytest.raises(NodeNotFoundError):
            g.neighbors("X")

    def test_neighbors_returns_copy(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        nb = g.neighbors("A")
        nb.add("X")  # mutate the copy
        assert "X" not in g.neighbors("A")  # original unchanged


class TestGraphBFS:
    def test_bfs_simple_path(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert list(g.bfs("A")) == ["A", "B", "C"]

    def test_bfs_unknown_start_raises(self) -> None:
        g: Graph[str] = Graph()
        with pytest.raises(NodeNotFoundError):
            list(g.bfs("Z"))


class TestGraphDFS:
    def test_dfs_simple_path(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        result = list(g.dfs("A"))
        assert result[0] == "A"
        assert set(result) == {"A", "B", "C"}

    def test_dfs_unknown_start_raises(self) -> None:
        g: Graph[str] = Graph()
        with pytest.raises(NodeNotFoundError):
            list(g.dfs("Z"))


class TestGraphHasCycle:
    def test_acyclic_undirected(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert g.has_cycle() is False

    def test_cyclic_undirected(self) -> None:
        g: Graph[str] = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        assert g.has_cycle() is True

    def test_acyclic_directed(self) -> None:
        g: Graph[str] = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert g.has_cycle() is False

    def test_cyclic_directed(self) -> None:
        g: Graph[str] = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        assert g.has_cycle() is True

    def test_empty_graph_no_cycle(self) -> None:
        g: Graph[str] = Graph()
        assert g.has_cycle() is False
