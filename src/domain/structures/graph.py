"""Adjacency-list graph (directed or undirected).

``Graph[T]`` models a set of nodes connected by edges.  Internally it uses a
``dict[T, set[T]]`` as an adjacency list — simple, memory-efficient for
sparse graphs, and O(1) average for node / edge existence tests.

    directed=False (default) – for every edge (u, v), (v, u) is also stored.
    directed=True            – edges are one-way.

``__iter__`` / ``size`` / ``contains`` iterate over **nodes** (not edges)
so the class satisfies the ``BaseStructure`` contract.

BFS and DFS both accept a *start* node and yield nodes in visit order.

``has_cycle()`` works for both directed (DFS with recursion stack) and
undirected graphs (DFS with parent tracking).

Complexity (n = nodes, m = edges):
    - add_node    : O(1)
    - add_edge    : O(1)
    - remove_node : O(n + m)  – must purge all references
    - remove_edge : O(1)
    - bfs / dfs   : O(n + m)
    - has_cycle   : O(n + m)
"""
from __future__ import annotations

from collections import deque
from typing import Generic, Iterator, TypeVar

from .base_structure import BaseStructure
from .exceptions import NodeNotFoundError

T = TypeVar("T")


class Graph(BaseStructure[T]):
    """Generic adjacency-list graph.

    Args:
        directed: When ``True`` edges are one-directional.  Default: ``False``.

    Example::

        g: Graph[str] = Graph()
        g.add_node("A")
        g.add_node("B")
        g.add_node("C")
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        print(list(g.bfs("A")))   # ['A', 'B', 'C']
        print(g.has_cycle())      # False
    """

    def __init__(self, directed: bool = False) -> None:
        self._directed: bool = directed
        # adjacency list: node → set of neighbours
        self._adj: dict[T, set[T]] = {}

    # ------------------------------------------------------------------ #
    # BaseStructure contract (iterates over nodes)                         #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        return iter(self._adj)

    def size(self) -> int:
        return len(self._adj)

    def contains(self, value: T) -> bool:
        return value in self._adj

    # ------------------------------------------------------------------ #
    # Mutating operations — nodes                                          #
    # ------------------------------------------------------------------ #

    def add_node(self, value: T) -> None:
        """Add *value* as a node (idempotent — no error if already present)."""
        self._adj.setdefault(value, set())

    def remove_node(self, value: T) -> bool:
        """Remove *value* and all its incident edges.

        Returns:
            True  – node existed and was removed.
            False – node not found.
        """
        if value not in self._adj:
            return False

        del self._adj[value]
        # Purge back-references in all remaining neighbours
        for neighbours in self._adj.values():
            neighbours.discard(value)

        return True

    # ------------------------------------------------------------------ #
    # Mutating operations — edges                                          #
    # ------------------------------------------------------------------ #

    def add_edge(self, source: T, destination: T) -> None:
        """Add an edge between *source* and *destination*.

        Both nodes are created automatically if they do not exist yet.

        Raises:
            NodeNotFoundError: Never — nodes are created implicitly.
        """
        self.add_node(source)
        self.add_node(destination)
        self._adj[source].add(destination)
        if not self._directed:
            self._adj[destination].add(source)

    def remove_edge(self, source: T, destination: T) -> bool:
        """Remove the edge from *source* to *destination*.

        Returns:
            True  – edge existed and was removed.
            False – edge not found.
        """
        if source not in self._adj or destination not in self._adj[source]:
            return False

        self._adj[source].discard(destination)
        if not self._directed:
            self._adj[destination].discard(source)

        return True

    # ------------------------------------------------------------------ #
    # Queries                                                              #
    # ------------------------------------------------------------------ #

    def neighbors(self, value: T) -> set[T]:
        """Return the set of immediate neighbours of *value*.

        Raises:
            NodeNotFoundError: When *value* is not in the graph.
        """
        if value not in self._adj:
            raise NodeNotFoundError(f"Node '{value}' not found.")
        return set(self._adj[value])

    # ------------------------------------------------------------------ #
    # Traversals                                                           #
    # ------------------------------------------------------------------ #

    def bfs(self, start: T) -> Iterator[T]:
        """Breadth-first traversal from *start*.

        Raises:
            NodeNotFoundError: When *start* is not in the graph.
        """
        if start not in self._adj:
            raise NodeNotFoundError(f"Start node '{start}' not found.")

        visited: set[T] = set()
        queue: deque[T] = deque([start])
        visited.add(start)

        while queue:
            node = queue.popleft()
            yield node
            for neighbour in sorted(self._adj[node], key=str):  # deterministic order
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    def dfs(self, start: T) -> Iterator[T]:
        """Depth-first traversal from *start*.

        Raises:
            NodeNotFoundError: When *start* is not in the graph.
        """
        if start not in self._adj:
            raise NodeNotFoundError(f"Start node '{start}' not found.")

        visited: set[T] = set()
        stack: list[T] = [start]

        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            yield node
            for neighbour in sorted(self._adj[node], key=str, reverse=True):
                if neighbour not in visited:
                    stack.append(neighbour)

    def has_cycle(self) -> bool:
        """Detect whether the graph contains at least one cycle.

        Uses DFS with a *recursion stack* for directed graphs and
        *parent tracking* for undirected graphs.
        """
        visited: set[T] = set()

        if self._directed:
            return self._has_cycle_directed(visited)
        else:
            return self._has_cycle_undirected(visited)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _has_cycle_directed(self, visited: set[T]) -> bool:
        rec_stack: set[T] = set()

        def dfs_visit(node: T) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbour in self._adj[node]:
                if neighbour not in visited:
                    if dfs_visit(neighbour):
                        return True
                elif neighbour in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        return any(dfs_visit(n) for n in self._adj if n not in visited)

    def _has_cycle_undirected(self, visited: set[T]) -> bool:
        def dfs_visit(node: T, parent: T | None) -> bool:
            visited.add(node)
            for neighbour in self._adj[node]:
                if neighbour not in visited:
                    if dfs_visit(neighbour, node):
                        return True
                elif neighbour != parent:
                    return True
            return False

        return any(dfs_visit(n, None) for n in self._adj if n not in visited)
