"""Queue (File) — FIFO structure.

Data Structure: **Queue** (First-In, First-Out).

Internally backed by a singly linked list for O(1) enqueue and O(1) dequeue
(using head + tail pointers). No dependency on ``collections.deque``.

    enqueue(v)  → insert at tail   — O(1)
    dequeue()   → remove from head — O(1)
    peek()      → read head        — O(1)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

from src.domain.structures.base_structure import BaseStructure

T = TypeVar("T")


@dataclass
class _QNode(Generic[T]):
    """Internal node for the Queue linked list."""

    value: T
    next: Optional[_QNode[T]] = None


class Queue(BaseStructure[T]):
    """FIFO Queue backed by a singly linked list with head + tail pointers.

    Complexity
    ----------
    ========== ====
    enqueue    O(1)
    dequeue    O(1)
    peek       O(1)
    contains   O(n)
    ========== ====
    """

    def __init__(self) -> None:
        self._head: Optional[_QNode[T]] = None
        self._tail: Optional[_QNode[T]] = None
        self._size: int = 0

    # -- Mutators --------------------------------------------------------- #

    def enqueue(self, value: T) -> None:
        """Add *value* at the back of the queue (tail) — O(1)."""
        node: _QNode[T] = _QNode(value=value)
        if self._tail is not None:
            self._tail.next = node
        self._tail = node
        if self._head is None:
            self._head = node
        self._size += 1

    def dequeue(self) -> T:
        """Remove and return the front element (head) — O(1).

        Raises
        ------
        IndexError
            If the queue is empty.
        """
        if self._head is None:
            raise IndexError("dequeue from an empty queue")
        value = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return value

    # -- Observers -------------------------------------------------------- #

    def peek(self) -> T:
        """Return the front element without removing it — O(1).

        Raises
        ------
        IndexError
            If the queue is empty.
        """
        if self._head is None:
            raise IndexError("peek on an empty queue")
        return self._head.value

    # -- BaseStructure contract ------------------------------------------- #

    def __iter__(self) -> Iterator[T]:
        """Iterate from head (front) to tail (back)."""
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def size(self) -> int:
        return self._size

    def contains(self, value: T) -> bool:
        current = self._head
        while current is not None:
            if current.value == value:
                return True
            current = current.next
        return False
