"""Unit tests for Tree (parametric N-ary tree)."""
from __future__ import annotations

import pytest

from src.domain.structures import Tree
from src.domain.structures.exceptions import ChildLimitExceededError, NodeNotFoundError


class TestTreeSemanticDescriptors:
    def test_linked_list_mode(self) -> None:
        t: Tree[int] = Tree(max_children=1)
        assert t.is_linked_list() is True
        assert t.is_binary_tree() is False

    def test_binary_tree_mode(self) -> None:
        t: Tree[int] = Tree(max_children=2)
        assert t.is_binary_tree() is True
        assert t.is_linked_list() is False

    def test_nary_tree_mode(self) -> None:
        t: Tree[int] = Tree(max_children=4)
        assert t.is_binary_tree() is False
        assert t.is_linked_list() is False

    def test_unbounded_tree(self) -> None:
        t: Tree[int] = Tree()
        assert t.is_binary_tree() is False
        assert t.is_linked_list() is False

    def test_invalid_max_children_raises(self) -> None:
        with pytest.raises(ValueError):
            Tree(max_children=0)


class TestTreeInsertAndSize:
    def test_insert_root(self) -> None:
        t: Tree[int] = Tree()
        t.insert(10)
        assert t.size() == 1
        assert t.contains(10)

    def test_insert_duplicate_root_raises(self) -> None:
        t: Tree[int] = Tree()
        t.insert(10)
        with pytest.raises(ValueError):
            t.insert(99)  # second root attempt without parent

    def test_insert_children(self) -> None:
        t: Tree[int] = Tree(max_children=2)
        t.insert(1)
        t.insert(2, parent_value=1)
        t.insert(3, parent_value=1)
        assert t.size() == 3
        assert t.contains(2)
        assert t.contains(3)

    def test_insert_unknown_parent_raises(self) -> None:
        t: Tree[int] = Tree()
        t.insert(1)
        with pytest.raises(NodeNotFoundError):
            t.insert(99, parent_value=42)

    def test_child_limit_exceeded_raises(self) -> None:
        t: Tree[int] = Tree(max_children=2)
        t.insert(1)
        t.insert(2, parent_value=1)
        t.insert(3, parent_value=1)
        with pytest.raises(ChildLimitExceededError):
            t.insert(4, parent_value=1)  # third child — forbidden


class TestTreeLinkedListMode:
    """max_children=1 → chain behaviour."""

    def test_chain_insertion(self) -> None:
        t: Tree[str] = Tree(max_children=1)
        t.insert("a")
        t.insert("b", parent_value="a")
        t.insert("c", parent_value="b")
        assert list(t) == ["a", "b", "c"]

    def test_chain_disallows_second_child(self) -> None:
        t: Tree[str] = Tree(max_children=1)
        t.insert("a")
        t.insert("b", parent_value="a")
        with pytest.raises(ChildLimitExceededError):
            t.insert("c", parent_value="a")  # "a" already has one child


class TestTreeBinaryMode:
    def test_binary_tree_structure(self) -> None:
        bt: Tree[int] = Tree(max_children=2)
        bt.insert(10)
        bt.insert(5, parent_value=10)
        bt.insert(15, parent_value=10)
        assert bt.size() == 3
        assert bt.depth() == 2

    def test_binary_tree_bfs_order(self) -> None:
        bt: Tree[int] = Tree(max_children=2)
        bt.insert(1)
        bt.insert(2, parent_value=1)
        bt.insert(3, parent_value=1)
        assert list(bt.bfs()) == [1, 2, 3]

    def test_binary_tree_dfs_order(self) -> None:
        bt: Tree[int] = Tree(max_children=2)
        bt.insert(1)
        bt.insert(2, parent_value=1)
        bt.insert(3, parent_value=1)
        # DFS pre-order: root, then left subtree, then right subtree
        assert list(bt.dfs()) == [1, 2, 3]


class TestTreeRemove:
    def test_remove_leaf(self) -> None:
        t: Tree[int] = Tree()
        t.insert(1)
        t.insert(2, parent_value=1)
        t.insert(3, parent_value=1)
        t.remove(3)
        assert t.size() == 2
        assert not t.contains(3)

    def test_remove_subtree(self) -> None:
        t: Tree[int] = Tree()
        t.insert(1)
        t.insert(2, parent_value=1)
        t.insert(4, parent_value=2)
        t.insert(5, parent_value=2)
        t.insert(3, parent_value=1)
        # Removing node 2 should also remove 4 and 5
        t.remove(2)
        assert t.size() == 2  # only 1 and 3 remain
        assert not t.contains(4)
        assert not t.contains(5)

    def test_remove_root(self) -> None:
        t: Tree[int] = Tree()
        t.insert(1)
        t.remove(1)
        assert t.is_empty()

    def test_remove_missing_returns_false(self) -> None:
        t: Tree[int] = Tree()
        t.insert(1)
        assert t.remove(99) is False

    def test_remove_from_empty_returns_false(self) -> None:
        t: Tree[int] = Tree()
        assert t.remove(1) is False


class TestTreeDepth:
    def test_empty_depth(self) -> None:
        t: Tree[int] = Tree()
        assert t.depth() == 0

    def test_single_node_depth(self) -> None:
        t: Tree[int] = Tree()
        t.insert(1)
        assert t.depth() == 1

    def test_chain_depth(self) -> None:
        t: Tree[int] = Tree(max_children=1)
        for i in range(1, 6):
            if i == 1:
                t.insert(i)
            else:
                t.insert(i, parent_value=i - 1)
        assert t.depth() == 5
