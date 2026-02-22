"""Unit tests for Queue (FIFO)."""
from __future__ import annotations

import pytest

from src.domain.structures.queue import Queue


class TestQueueBasics:
    def test_new_queue_is_empty(self) -> None:
        q: Queue[int] = Queue()
        assert q.is_empty()
        assert q.size() == 0
        assert len(q) == 0

    def test_enqueue_single(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(42)
        assert q.size() == 1
        assert not q.is_empty()

    def test_fifo_order(self) -> None:
        q: Queue[str] = Queue()
        q.enqueue("a")
        q.enqueue("b")
        q.enqueue("c")
        assert q.dequeue() == "a"
        assert q.dequeue() == "b"
        assert q.dequeue() == "c"

    def test_enqueue_dequeue_interleaved(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(1)
        q.enqueue(2)
        assert q.dequeue() == 1
        q.enqueue(3)
        assert q.dequeue() == 2
        assert q.dequeue() == 3
        assert q.is_empty()


class TestQueueDequeue:
    def test_dequeue_empty_raises(self) -> None:
        q: Queue[int] = Queue()
        with pytest.raises(IndexError):
            q.dequeue()

    def test_dequeue_all_then_enqueue(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(1)
        q.dequeue()
        q.enqueue(2)
        assert q.peek() == 2


class TestQueuePeek:
    def test_peek_returns_front(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(10)
        q.enqueue(20)
        assert q.peek() == 10

    def test_peek_does_not_remove(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(10)
        q.peek()
        assert q.size() == 1

    def test_peek_empty_raises(self) -> None:
        q: Queue[int] = Queue()
        with pytest.raises(IndexError):
            q.peek()


class TestQueueIteration:
    def test_iter_order(self) -> None:
        q: Queue[int] = Queue()
        for v in [1, 2, 3, 4]:
            q.enqueue(v)
        assert list(q) == [1, 2, 3, 4]

    def test_iter_empty(self) -> None:
        q: Queue[int] = Queue()
        assert list(q) == []


class TestQueueContains:
    def test_contains_present(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(5)
        q.enqueue(10)
        assert q.contains(10)

    def test_contains_absent(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(5)
        assert not q.contains(99)

    def test_contains_empty(self) -> None:
        q: Queue[int] = Queue()
        assert not q.contains(1)


class TestQueueRepr:
    def test_repr(self) -> None:
        q: Queue[int] = Queue()
        q.enqueue(1)
        r = repr(q)
        assert "Queue" in r
        assert "1" in r
