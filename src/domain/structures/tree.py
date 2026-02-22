"""Parametric N-ary tree.

A single ``Tree[T]`` class covers three use-cases controlled by the
``max_children`` constructor parameter:

    max_children=1   → behaves like a **linked list** (chain of single children)
    max_children=2   → **binary tree**
    max_children=N   → general **N-ary tree**
    max_children=None→ unbounded tree

Semantic helpers ``is_linked_list()`` and ``is_binary_tree()`` let callers
ask *what kind* of tree they have without any isinstance checks.

Iteration order is BFS by default (``__iter__``). DFS is available via
``dfs()``.

Complexity overview (n = number of nodes):
    - insert  : O(n) – BFS scan to find parent
    - remove  : O(n) – BFS scan + parent re-link
    - depth   : O(n) – full traversal
    - bfs/dfs : O(n)
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Generic, Iterator, Optional, TypeVar

from .base_structure import BaseStructure
from .exceptions import ChildLimitExceededError, NodeNotFoundError

T = TypeVar("T")


@dataclass
class _TreeNode(Generic[T]):
    """Internal tree node.  Not part of the public API."""

    value: T
    children: list["_TreeNode[T]"] = field(default_factory=list, repr=False)


class Tree(BaseStructure[T]):
    """Generic parametric N-ary tree.

    Args:
        max_children: Maximum number of children per node.
            - ``1``    → linked-list-like chain
            - ``2``    → binary tree
            - ``N``    → N-ary tree
            - ``None`` → unbounded (default)

    Example::

        # Binary tree
        bt: Tree[int] = Tree(max_children=2)
        bt.insert(10)
        bt.insert(5, parent_value=10)
        bt.insert(15, parent_value=10)
        print(list(bt))  # [10, 5, 15]  (BFS)
        print(bt.is_binary_tree())  # True

        # Linked-list-like chain
        chain: Tree[str] = Tree(max_children=1)
        chain.insert("a")
        chain.insert("b", parent_value="a")
        chain.insert("c", parent_value="b")
        print(list(chain))  # ['a', 'b', 'c']
        print(chain.is_linked_list())  # True
    """

    def __init__(self, max_children: Optional[int] = None) -> None:
        if max_children is not None and max_children < 1:
            raise ValueError("max_children must be >= 1 or None.")
        self._max_children: Optional[int] = max_children
        self._root: Optional[_TreeNode[T]] = None
        self._size: int = 0

    # ------------------------------------------------------------------ #
    # Semantic descriptors                                                 #
    # ------------------------------------------------------------------ #

    def is_linked_list(self) -> bool:
        """True when every node may have at most 1 child."""
        return self._max_children == 1

    def is_binary_tree(self) -> bool:
        """True when every node may have at most 2 children."""
        return self._max_children == 2

    # ------------------------------------------------------------------ #
    # BaseStructure contract                                               #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        """BFS iteration (level-order)."""
        return self.bfs()

    def size(self) -> int:
        return self._size

    def contains(self, value: T) -> bool:
        return any(v == value for v in self)

    # ------------------------------------------------------------------ #
    # Mutating operations                                                  #
    # ------------------------------------------------------------------ #

    def insert(self, value: T, parent_value: Optional[T] = None) -> None:
        """Insert *value* into the tree.

        Args:
            value:        The value to store.
            parent_value: Parent node value.  If ``None`` the node becomes
                          the root (only allowed when the tree is empty).

        Raises:
            NodeNotFoundError:       When *parent_value* is not found.
            ChildLimitExceededError: When the parent already has
                                     ``max_children`` children.
            ValueError:              When inserting a root into a non-empty tree.
        """
        new_node: _TreeNode[T] = _TreeNode(value=value)

        if parent_value is None:
            if self._root is not None:
                raise ValueError(
                    "Tree already has a root. Provide a parent_value."
                )
            self._root = new_node
            self._size += 1
            return

        parent = self._find_node(parent_value)
        if parent is None:
            raise NodeNotFoundError(f"Parent node '{parent_value}' not found.")

        if (
            self._max_children is not None
            and len(parent.children) >= self._max_children
        ):
            raise ChildLimitExceededError(
                f"Node '{parent_value}' already has {self._max_children} "
                f"child(ren) — max_children={self._max_children}."
            )

        parent.children.append(new_node)
        self._size += 1

    def remove(self, value: T) -> bool:
        """Remove the **first** node with *value* (BFS order).

        Removing a node also removes its entire subtree.

        Returns:
            True  – node found and removed.
            False – node not found, tree unchanged.
        """
        if self._root is None:
            return False

        if self._root.value == value:
            subtree_size = self._count_subtree(self._root)
            self._root = None
            self._size -= subtree_size
            return True

        # BFS to find the parent of the target node
        queue: deque[_TreeNode[T]] = deque([self._root])
        while queue:
            current = queue.popleft()
            for idx, child in enumerate(current.children):
                if child.value == value:
                    subtree_size = self._count_subtree(child)
                    current.children.pop(idx)
                    self._size -= subtree_size
                    return True
                queue.append(child)

        return False

    # ------------------------------------------------------------------ #
    # Traversals                                                           #
    # ------------------------------------------------------------------ #

    def bfs(self) -> Iterator[T]:
        """Breadth-first (level-order) traversal."""
        if self._root is None:
            return
        queue: deque[_TreeNode[T]] = deque([self._root])
        while queue:
            node = queue.popleft()
            yield node.value
            queue.extend(node.children)

    def dfs(self) -> Iterator[T]:
        """Depth-first (pre-order) traversal."""
        if self._root is None:
            return
        stack: list[_TreeNode[T]] = [self._root]
        while stack:
            node = stack.pop()
            yield node.value
            # Push children in reverse so left-most child is processed first
            stack.extend(reversed(node.children))

    def depth(self) -> int:
        """Return the maximum depth of the tree (root is depth 1, empty is 0)."""
        if self._root is None:
            return 0
        return self._depth_recursive(self._root)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _find_node(self, value: T) -> Optional[_TreeNode[T]]:
        """BFS search — returns the first node whose value == *value*."""
        if self._root is None:
            return None
        queue: deque[_TreeNode[T]] = deque([self._root])
        while queue:
            node = queue.popleft()
            if node.value == value:
                return node
            queue.extend(node.children)
        return None

    def _depth_recursive(self, node: _TreeNode[T]) -> int:
        if not node.children:
            return 1
        return 1 + max(self._depth_recursive(c) for c in node.children)

    def _count_subtree(self, node: _TreeNode[T]) -> int:
        """Count nodes in the subtree rooted at *node* (inclusive)."""
        return 1 + sum(self._count_subtree(c) for c in node.children)
