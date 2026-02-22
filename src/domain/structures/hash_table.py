"""HashTable (Dictionnaire) — open-addressing hash map.

Data Structure: **Hash Table** (dictionary / associative array).

Custom implementation using **open addressing with linear probing**.
Does NOT wrap Python's built-in ``dict``; it uses a plain ``list`` of
buckets and implements hashing, collision resolution, and dynamic resizing
from scratch.

    put(k, v)      → insert or update  — amortised O(1)
    get(k)         → lookup            — amortised O(1)
    remove(k)      → delete            — amortised O(1)
    contains_key   → key lookup        — amortised O(1)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

from src.domain.structures.base_structure import BaseStructure

K = TypeVar("K")
V = TypeVar("V")

_EMPTY = object()       # sentinel: slot never used
_DELETED = object()     # sentinel: slot was used then removed (tombstone)

_INITIAL_CAPACITY = 8
_LOAD_FACTOR = 0.7      # resize when len / capacity exceeds this


@dataclass
class _Entry(Generic[K, V]):
    """A single key-value bucket."""

    key: K
    value: V


class HashTable(BaseStructure[tuple[K, V]], Generic[K, V]):
    """Hash map using open addressing with linear probing.

    The ``BaseStructure`` type parameter is ``tuple[K, V]`` so that
    ``__iter__`` yields ``(key, value)`` pairs and ``contains()`` checks
    for a key-value pair — consistent with the base contract.

    Complexity (amortised)
    ----------------------
    ========== ====
    put        O(1)
    get        O(1)
    remove     O(1)
    ========== ====
    """

    def __init__(self, capacity: int = _INITIAL_CAPACITY) -> None:
        self._capacity: int = max(capacity, _INITIAL_CAPACITY)
        self._slots: list[object] = [_EMPTY] * self._capacity
        self._size: int = 0

    # -- Mutators --------------------------------------------------------- #

    def put(self, key: K, value: V) -> None:
        """Insert or update *key* → *value*. Resizes if load factor exceeded."""
        if (self._size + 1) / self._capacity > _LOAD_FACTOR:
            self._resize(self._capacity * 2)
        self._do_put(key, value)

    def remove(self, key: K) -> bool:
        """Remove *key*. Returns ``True`` if it existed, ``False`` otherwise."""
        idx = self._find_slot(key)
        if idx is None:
            return False
        self._slots[idx] = _DELETED
        self._size -= 1
        return True

    # -- Observers -------------------------------------------------------- #

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return the value for *key*, or *default* if not found."""
        idx = self._find_slot(key)
        if idx is None:
            return default
        entry: _Entry[K, V] = self._slots[idx]  # type: ignore[assignment]
        return entry.value

    def contains_key(self, key: K) -> bool:
        """Return ``True`` if *key* is present."""
        return self._find_slot(key) is not None

    def keys(self) -> list[K]:
        """Return a list of all keys."""
        return [
            s.key for s in self._slots  # type: ignore[union-attr]
            if isinstance(s, _Entry)
        ]

    def values(self) -> list[V]:
        """Return a list of all values."""
        return [
            s.value for s in self._slots  # type: ignore[union-attr]
            if isinstance(s, _Entry)
        ]

    # -- BaseStructure contract ------------------------------------------- #

    def __iter__(self) -> Iterator[tuple[K, V]]:
        """Yield ``(key, value)`` pairs in insertion-ish order."""
        for slot in self._slots:
            if isinstance(slot, _Entry):
                yield (slot.key, slot.value)

    def size(self) -> int:
        return self._size

    def contains(self, value: tuple[K, V]) -> bool:
        """Check if ``(key, val)`` pair exists in the table."""
        key, val = value
        idx = self._find_slot(key)
        if idx is None:
            return False
        entry: _Entry[K, V] = self._slots[idx]  # type: ignore[assignment]
        return entry.value == val

    # -- Internal --------------------------------------------------------- #

    def _hash(self, key: K) -> int:
        return hash(key) % self._capacity

    def _do_put(self, key: K, value: V) -> None:
        idx = self._hash(key)
        while True:
            slot = self._slots[idx]
            if slot is _EMPTY or slot is _DELETED:
                self._slots[idx] = _Entry(key=key, value=value)
                self._size += 1
                return
            if isinstance(slot, _Entry) and slot.key == key:
                # Update existing
                self._slots[idx] = _Entry(key=key, value=value)
                return
            idx = (idx + 1) % self._capacity

    def _find_slot(self, key: K) -> Optional[int]:
        """Return the index of *key*, or ``None``."""
        idx = self._hash(key)
        for _ in range(self._capacity):
            slot = self._slots[idx]
            if slot is _EMPTY:
                return None
            if isinstance(slot, _Entry) and slot.key == key:
                return idx
            idx = (idx + 1) % self._capacity
        return None

    def _resize(self, new_capacity: int) -> None:
        old_slots = self._slots
        self._capacity = new_capacity
        self._slots = [_EMPTY] * self._capacity
        self._size = 0
        for slot in old_slots:
            if isinstance(slot, _Entry):
                self._do_put(slot.key, slot.value)
