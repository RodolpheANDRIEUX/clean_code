"""Tests for Time domain model."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from src.domain.model.time import UtcTimestamp, TimeWindow


class TestUtcTimestamp:
    """Tests for UtcTimestamp value object."""

    def test_valid_utc_timestamp(self) -> None:
        dt = datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)
        ts = UtcTimestamp(value=dt)
        assert ts.value == dt

    def test_timestamp_normalized_to_utc(self) -> None:
        # Create a datetime with +01:00 offset
        dt_paris = datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone(timedelta(hours=1)))
        ts = UtcTimestamp(value=dt_paris)
        # Should be normalized to UTC (9:00)
        assert ts.value.hour == 9
        assert ts.value.tzinfo == timezone.utc

    def test_timestamp_immutable(self) -> None:
        dt = datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)
        ts = UtcTimestamp(value=dt)
        with pytest.raises(AttributeError):
            ts.value = datetime.now(timezone.utc)  # type: ignore

    def test_timestamp_requires_timezone_aware(self) -> None:
        dt_naive = datetime(2025, 12, 1, 9, 0, 0)
        with pytest.raises(ValueError, match="timezone-aware"):
            UtcTimestamp(value=dt_naive)

    def test_from_iso8601_with_offset(self) -> None:
        ts = UtcTimestamp.from_iso8601("2025-12-01T09:00:00+00:00")
        assert ts.value.year == 2025
        assert ts.value.month == 12
        assert ts.value.day == 1
        assert ts.value.hour == 9

    def test_from_iso8601_with_z(self) -> None:
        ts = UtcTimestamp.from_iso8601("2025-12-01T09:00:00Z")
        assert ts.value.year == 2025
        assert ts.value.hour == 9
        assert ts.value.tzinfo == timezone.utc

    def test_from_iso8601_with_different_offset(self) -> None:
        ts = UtcTimestamp.from_iso8601("2025-12-01T10:00:00+01:00")
        # Should be normalized to UTC (9:00)
        assert ts.value.hour == 9

    def test_from_iso8601_invalid_empty(self) -> None:
        with pytest.raises(ValueError, match="ISO8601 invalide"):
            UtcTimestamp.from_iso8601("")

    def test_from_iso8601_invalid_whitespace(self) -> None:
        with pytest.raises(ValueError, match="ISO8601 invalide"):
            UtcTimestamp.from_iso8601("   ")

    def test_is_in_future_true(self) -> None:
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        future = UtcTimestamp(datetime(2025, 12, 1, 9, 10, 0, tzinfo=timezone.utc))
        assert future.is_in_future(now=now)

    def test_is_in_future_false(self) -> None:
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        past = UtcTimestamp(datetime(2025, 12, 1, 8, 50, 0, tzinfo=timezone.utc))
        assert not past.is_in_future(now=now)

    def test_is_in_future_with_tolerance(self) -> None:
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        # 3 minutes in future, but within 5 minute tolerance
        near_future = UtcTimestamp(datetime(2025, 12, 1, 9, 3, 0, tzinfo=timezone.utc))
        assert not near_future.is_in_future(now=now, tolerance=timedelta(minutes=5))

    def test_is_in_future_beyond_tolerance(self) -> None:
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        # 6 minutes in future, beyond 5 minute tolerance
        far_future = UtcTimestamp(datetime(2025, 12, 1, 9, 6, 0, tzinfo=timezone.utc))
        assert far_future.is_in_future(now=now, tolerance=timedelta(minutes=5))

    def test_str_representation(self) -> None:
        dt = datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)
        ts = UtcTimestamp(value=dt)
        assert "2025-12-01" in str(ts)
        assert "09:00:00" in str(ts)


class TestTimeWindow:
    """Tests for TimeWindow value object."""

    def test_valid_time_window(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        assert window.start == start
        assert window.end == end

    def test_time_window_immutable(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        with pytest.raises(AttributeError):
            window.start = end  # type: ignore

    def test_time_window_start_after_end(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        with pytest.raises(ValueError, match="start doit être strictement < end"):
            TimeWindow(start=start, end=end)

    def test_time_window_start_equals_end(self) -> None:
        dt = datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)
        start = UtcTimestamp(dt)
        end = UtcTimestamp(dt)
        with pytest.raises(ValueError, match="start doit être strictement < end"):
            TimeWindow(start=start, end=end)

    def test_contains_timestamp_inside(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        
        inside = UtcTimestamp(datetime(2025, 12, 1, 9, 30, 0, tzinfo=timezone.utc))
        assert window.contains(inside)

    def test_contains_timestamp_at_start(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        assert window.contains(start)

    def test_contains_timestamp_at_end(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        # End is exclusive
        assert not window.contains(end)

    def test_contains_timestamp_before(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        
        before = UtcTimestamp(datetime(2025, 12, 1, 8, 0, 0, tzinfo=timezone.utc))
        assert not window.contains(before)

    def test_contains_timestamp_after(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        
        after = UtcTimestamp(datetime(2025, 12, 1, 11, 0, 0, tzinfo=timezone.utc))
        assert not window.contains(after)

    def test_duration(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        assert window.duration() == timedelta(hours=1)

    def test_duration_multiple_days(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 3, 9, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        assert window.duration() == timedelta(days=2)

    def test_str_representation(self) -> None:
        start = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        end = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        window = TimeWindow(start=start, end=end)
        window_str = str(window)
        assert "2025-12-01" in window_str
        assert "→" in window_str
