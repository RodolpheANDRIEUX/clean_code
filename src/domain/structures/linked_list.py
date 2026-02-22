"""Singly linked list implementation.

A ``LinkedList[T]`` is the simplest concrete ``BaseStructure[T]``:
a chain of ``_Node`` cells where each cell holds a value and a pointer
to the next cell.

Complexity overview:
    - prepend : O(1)
    - append  : O(n)  – we walk to the tail
    - remove  : O(n)  – linear scan
    - contains: O(n)  – linear scan
    - size    : O(1)  – maintained by a counter
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Iterator, Optional, TypeVar

from .base_structure import BaseStructure

T = TypeVar("T")


@dataclass
class _Node(Generic[T]):
    """Internal singly-linked node.  Not part of the public API."""

    value: T
    next: Optional["_Node[T]"] = field(default=None, repr=False)


class LinkedList(BaseStructure[T]):
    """Generic singly linked list.

    Example::

        lst: LinkedList[int] = LinkedList()
        lst.append(1)
        lst.append(2)
        lst.prepend(0)
        print(list(lst))   # [0, 1, 2]
        lst.remove(1)
        print(list(lst))   # [0, 2]
    """

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._size: int = 0

    # ------------------------------------------------------------------ #
    # BaseStructure contract                                               #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def size(self) -> int:
        return self._size

    def contains(self, value: T) -> bool:
        return any(v == value for v in self)

    # ------------------------------------------------------------------ #
    # Mutating operations                                                  #
    # ------------------------------------------------------------------ #

    def prepend(self, value: T) -> None:
        """Insert *value* at the head — O(1)."""
        self._head = _Node(value=value, next=self._head)
        self._size += 1

    def append(self, value: T) -> None:
        """Insert *value* at the tail — O(n)."""
        new_node: _Node[T] = _Node(value=value)
        if self._head is None:
            self._head = new_node
        else:
            current = self._head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def remove(self, value: T) -> bool:
        """Remove the **first** occurrence of *value*.

        Returns:
            True  – element found and removed.
            False – element not found, list unchanged.
        """
        if self._head is None:
            return False

        if self._head.value == value:
            self._head = self._head.next
            self._size -= 1
            return True

        current = self._head
        while current.next is not None:
            if current.next.value == value:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next

        return False

    # ------------------------------------------------------------------ #
    # Extras                                                               #
    # ------------------------------------------------------------------ #

    def to_list(self) -> list[T]:
        """Return a plain Python list snapshot of the current state."""
        return list(self)
