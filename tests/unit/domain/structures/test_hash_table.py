"""Unit tests for HashTable (custom dictionary with open addressing)."""
from __future__ import annotations

import pytest

from src.domain.structures.hash_table import HashTable


class TestHashTableBasics:
    def test_new_table_is_empty(self) -> None:
        ht: HashTable[str, int] = HashTable()
        assert ht.is_empty()
        assert ht.size() == 0
        assert len(ht) == 0

    def test_put_and_get(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("a", 1)
        assert ht.get("a") == 1
        assert ht.size() == 1

    def test_put_overwrite(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("a", 1)
        ht.put("a", 99)
        assert ht.get("a") == 99
        assert ht.size() == 1

    def test_get_missing_returns_default(self) -> None:
        ht: HashTable[str, int] = HashTable()
        assert ht.get("nope") is None
        assert ht.get("nope", -1) == -1


class TestHashTableRemove:
    def test_remove_existing(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("x", 10)
        assert ht.remove("x") is True
        assert ht.size() == 0
        assert ht.get("x") is None

    def test_remove_missing(self) -> None:
        ht: HashTable[str, int] = HashTable()
        assert ht.remove("nope") is False

    def test_put_after_remove(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("a", 1)
        ht.remove("a")
        ht.put("a", 2)
        assert ht.get("a") == 2
        assert ht.size() == 1


class TestHashTableContains:
    def test_contains_key(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("k", 42)
        assert ht.contains_key("k")
        assert not ht.contains_key("other")

    def test_contains_pair(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("k", 42)
        assert ht.contains(("k", 42))
        assert not ht.contains(("k", 99))


class TestHashTableIteration:
    def test_iter_yields_pairs(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("a", 1)
        ht.put("b", 2)
        pairs = set(ht)
        assert ("a", 1) in pairs
        assert ("b", 2) in pairs
        assert len(pairs) == 2

    def test_keys_and_values(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("x", 10)
        ht.put("y", 20)
        assert set(ht.keys()) == {"x", "y"}
        assert set(ht.values()) == {10, 20}


class TestHashTableResize:
    def test_handles_many_entries(self) -> None:
        ht: HashTable[int, int] = HashTable(capacity=8)
        for i in range(100):
            ht.put(i, i * 10)
        assert ht.size() == 100
        for i in range(100):
            assert ht.get(i) == i * 10

    def test_resize_preserves_data(self) -> None:
        ht: HashTable[str, str] = HashTable(capacity=8)
        for c in "abcdefghijklmnop":
            ht.put(c, c.upper())
        assert ht.size() == 16
        for c in "abcdefghijklmnop":
            assert ht.get(c) == c.upper()


class TestHashTableCollisions:
    def test_integer_key_collisions(self) -> None:
        ht: HashTable[int, str] = HashTable(capacity=8)
        # Keys that hash to the same bucket (mod 8)
        ht.put(0, "zero")
        ht.put(8, "eight")
        ht.put(16, "sixteen")
        assert ht.get(0) == "zero"
        assert ht.get(8) == "eight"
        assert ht.get(16) == "sixteen"
        assert ht.size() == 3


class TestHashTableRepr:
    def test_repr(self) -> None:
        ht: HashTable[str, int] = HashTable()
        ht.put("k", 1)
        r = repr(ht)
        assert "HashTable" in r
