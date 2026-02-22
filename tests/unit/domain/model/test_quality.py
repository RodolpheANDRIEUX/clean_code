"""Tests for Quality domain model."""
from __future__ import annotations

import pytest

from src.domain.model.quality import QualityFlag, QualityStatus


class TestQualityFlag:
    """Tests for QualityFlag enum."""

    def test_all_flags_exist(self) -> None:
        assert QualityFlag.MISSING_FIELD == "MISSING_FIELD"
        assert QualityFlag.OUT_OF_RANGE == "OUT_OF_RANGE"
        assert QualityFlag.FUTURE_TIMESTAMP == "FUTURE_TIMESTAMP"
        assert QualityFlag.DUPLICATE == "DUPLICATE"
        assert QualityFlag.PARSE_ERROR == "PARSE_ERROR"
        assert QualityFlag.INCONSISTENT_TIME == "INCONSISTENT_TIME"
        assert QualityFlag.UNKNOWN_STATION == "UNKNOWN_STATION"
        assert QualityFlag.UNKNOWN == "UNKNOWN"


class TestQualityStatus:
    """Tests for QualityStatus value object."""

    def test_ok_status(self) -> None:
        status = QualityStatus.ok()
        assert status.is_ok()
        assert len(status.flags) == 0

    def test_status_immutable(self) -> None:
        status = QualityStatus.ok()
        with pytest.raises(AttributeError):
            status.flags = frozenset({QualityFlag.MISSING_FIELD})  # type: ignore

    def test_from_flags_single(self) -> None:
        status = QualityStatus.from_flags([QualityFlag.MISSING_FIELD])
        assert not status.is_ok()
        assert status.has(QualityFlag.MISSING_FIELD)

    def test_from_flags_multiple(self) -> None:
        status = QualityStatus.from_flags([
            QualityFlag.MISSING_FIELD,
            QualityFlag.OUT_OF_RANGE,
        ])
        assert not status.is_ok()
        assert status.has(QualityFlag.MISSING_FIELD)
        assert status.has(QualityFlag.OUT_OF_RANGE)
        assert len(status.flags) == 2

    def test_from_flags_empty(self) -> None:
        status = QualityStatus.from_flags([])
        assert status.is_ok()

    def test_has_flag_true(self) -> None:
        status = QualityStatus.from_flags([QualityFlag.FUTURE_TIMESTAMP])
        assert status.has(QualityFlag.FUTURE_TIMESTAMP)

    def test_has_flag_false(self) -> None:
        status = QualityStatus.from_flags([QualityFlag.FUTURE_TIMESTAMP])
        assert not status.has(QualityFlag.MISSING_FIELD)

    def test_add_flag(self) -> None:
        status = QualityStatus.ok()
        new_status = status.add(QualityFlag.MISSING_FIELD)
        
        # Original unchanged (immutable)
        assert status.is_ok()
        
        # New status has the flag
        assert not new_status.is_ok()
        assert new_status.has(QualityFlag.MISSING_FIELD)

    def test_add_multiple_flags(self) -> None:
        status = QualityStatus.ok()
        status = status.add(QualityFlag.MISSING_FIELD)
        status = status.add(QualityFlag.OUT_OF_RANGE)
        
        assert status.has(QualityFlag.MISSING_FIELD)
        assert status.has(QualityFlag.OUT_OF_RANGE)
        assert len(status.flags) == 2

    def test_add_duplicate_flag(self) -> None:
        status = QualityStatus.from_flags([QualityFlag.MISSING_FIELD])
        new_status = status.add(QualityFlag.MISSING_FIELD)
        
        # Should still have only one flag (frozenset deduplicates)
        assert len(new_status.flags) == 1
        assert new_status.has(QualityFlag.MISSING_FIELD)

    def test_merge_ok_with_ok(self) -> None:
        status1 = QualityStatus.ok()
        status2 = QualityStatus.ok()
        merged = status1.merge(status2)
        assert merged.is_ok()

    def test_merge_ok_with_flags(self) -> None:
        status1 = QualityStatus.ok()
        status2 = QualityStatus.from_flags([QualityFlag.MISSING_FIELD])
        merged = status1.merge(status2)
        
        assert not merged.is_ok()
        assert merged.has(QualityFlag.MISSING_FIELD)

    def test_merge_flags_with_flags(self) -> None:
        status1 = QualityStatus.from_flags([QualityFlag.MISSING_FIELD])
        status2 = QualityStatus.from_flags([QualityFlag.OUT_OF_RANGE])
        merged = status1.merge(status2)
        
        assert merged.has(QualityFlag.MISSING_FIELD)
        assert merged.has(QualityFlag.OUT_OF_RANGE)
        assert len(merged.flags) == 2

    def test_merge_overlapping_flags(self) -> None:
        status1 = QualityStatus.from_flags([
            QualityFlag.MISSING_FIELD,
            QualityFlag.OUT_OF_RANGE,
        ])
        status2 = QualityStatus.from_flags([
            QualityFlag.OUT_OF_RANGE,
            QualityFlag.FUTURE_TIMESTAMP,
        ])
        merged = status1.merge(status2)
        
        assert merged.has(QualityFlag.MISSING_FIELD)
        assert merged.has(QualityFlag.OUT_OF_RANGE)
        assert merged.has(QualityFlag.FUTURE_TIMESTAMP)
        assert len(merged.flags) == 3

    def test_merge_immutability(self) -> None:
        status1 = QualityStatus.from_flags([QualityFlag.MISSING_FIELD])
        status2 = QualityStatus.from_flags([QualityFlag.OUT_OF_RANGE])
        merged = status1.merge(status2)
        
        # Original statuses unchanged
        assert len(status1.flags) == 1
        assert len(status2.flags) == 1
        
        # Merged has both
        assert len(merged.flags) == 2
