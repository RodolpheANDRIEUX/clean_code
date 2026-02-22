"""Unit tests for LinkedList."""
from __future__ import annotations

import pytest

from src.domain.structures import LinkedList


class TestLinkedListBasics:
    """Size, emptiness, repr."""

    def test_new_list_is_empty(self) -> None:
        lst: LinkedList[int] = LinkedList()
        assert lst.is_empty()
        assert lst.size() == 0
        assert len(lst) == 0

    def test_repr(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(1)
        assert "LinkedList" in repr(lst)
        assert "1" in repr(lst)


class TestLinkedListAppend:
    """Append — O(n) insertion at tail."""

    def test_append_single(self) -> None:
        lst: LinkedList[str] = LinkedList()
        lst.append("a")
        assert list(lst) == ["a"]
        assert lst.size() == 1

    def test_append_multiple_preserves_order(self) -> None:
        lst: LinkedList[int] = LinkedList()
        for v in [1, 2, 3]:
            lst.append(v)
        assert list(lst) == [1, 2, 3]

    def test_to_list_matches_iteration(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(10)
        lst.append(20)
        assert lst.to_list() == list(lst)


class TestLinkedListPrepend:
    """Prepend — O(1) insertion at head."""

    def test_prepend_single(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.prepend(5)
        assert list(lst) == [5]

    def test_prepend_multiple_reverses_insertion_order(self) -> None:
        lst: LinkedList[int] = LinkedList()
        for v in [1, 2, 3]:
            lst.prepend(v)
        assert list(lst) == [3, 2, 1]

    def test_prepend_then_append(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.prepend(2)
        lst.prepend(1)
        lst.append(3)
        assert list(lst) == [1, 2, 3]


class TestLinkedListRemove:
    """Remove — removes first occurrence."""

    def test_remove_existing_element(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        result = lst.remove(2)
        assert result is True
        assert list(lst) == [1, 3]
        assert lst.size() == 2

    def test_remove_head(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(1)
        lst.append(2)
        lst.remove(1)
        assert list(lst) == [2]

    def test_remove_tail(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(1)
        lst.append(2)
        lst.remove(2)
        assert list(lst) == [1]

    def test_remove_only_first_occurrence(self) -> None:
        lst: LinkedList[str] = LinkedList()
        lst.append("x")
        lst.append("x")
        lst.remove("x")
        assert list(lst) == ["x"]

    def test_remove_missing_returns_false(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(1)
        assert lst.remove(99) is False
        assert list(lst) == [1]

    def test_remove_from_empty_returns_false(self) -> None:
        lst: LinkedList[int] = LinkedList()
        assert lst.remove(42) is False


class TestLinkedListContains:
    def test_contains_present(self) -> None:
        lst: LinkedList[int] = LinkedList()
        lst.append(7)
        assert lst.contains(7) is True

    def test_contains_absent(self) -> None:
        lst: LinkedList[int] = LinkedList()
        assert lst.contains(7) is False
