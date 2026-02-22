"""Abstract base for all custom data structures.

Defines the minimal contract every structure must honour:
- size / emptiness
- membership test
- iteration
- repr
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class BaseStructure(ABC, Generic[T]):
    """Generic abstract base shared by LinkedList, Tree and Graph.

    Subclasses must implement:
        - ``__iter__``  – yields every element in a structure-specific order.
        - ``size``      – returns the number of elements.
        - ``contains``  – membership test.

    Everything else (``__len__``, ``is_empty``, ``__repr__``) is derived
    from those three primitives so concrete classes stay DRY.
    """

    # ------------------------------------------------------------------ #
    # Abstract interface                                                   #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Iterate over all values in structure-specific order."""

    @abstractmethod
    def size(self) -> int:
        """Return the number of elements stored."""

    @abstractmethod
    def contains(self, value: T) -> bool:
        """Return True if *value* is present in the structure."""

    # ------------------------------------------------------------------ #
    # Concrete helpers derived from the abstract interface                 #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """Return True when the structure holds no elements."""
        return self.size() == 0

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        name = type(self).__name__
        items = list(self)
        return f"{name}({items!r})"
