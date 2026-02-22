"""Tests for IngestToOds use case."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import pytest

from src.application.use_cases.ingest_to_ods import IngestToOds, IngestReport
from src.application.ports.clock import ClockPort
from src.application.ports.ods import OdsRepositoryPort, OdsBatch, OdsAppendResult
from src.application.ports.weather import WeatherRecordsPort, RawRecord
from src.domain.model.station import Station, StationId, DatasetId, StationType
from src.domain.model.time import TimeWindow, UtcTimestamp


@dataclass
class FakeClock:
    """Fake clock for testing."""
    current_time: UtcTimestamp

    def now_utc(self) -> UtcTimestamp:
        return self.current_time


@dataclass
class FakeWeatherRecords:
    """Fake weather records port."""
    records_by_station: dict[int, list[RawRecord]]

    def fetch_records(self, station: Station, window: TimeWindow) -> Iterable[RawRecord]:
        return self.records_by_station.get(station.id.value, [])


@dataclass
class FakeOdsRepository:
    """Fake ODS repository."""
    batches: list[OdsBatch]
    records: list[tuple[OdsBatch, Station, list[RawRecord]]]
    finished_batches: list[str]

    def __init__(self) -> None:
        self.batches = []
        self.records = []
        self.finished_batches = []

    def start_batch(self, *, window: TimeWindow, station_count: int, started_at: UtcTimestamp) -> OdsBatch:
        batch = OdsBatch(
            batch_id=f"batch-{len(self.batches)}",
            started_at=started_at,
            window=window,
            station_count=station_count,
        )
        self.batches.append(batch)
        return batch

    def append_station_records(
        self, *, batch: OdsBatch, station: Station, records: Iterable[RawRecord]
    ) -> OdsAppendResult:
        records_list = list(records)
        self.records.append((batch, station, records_list))
        return OdsAppendResult(inserted=len(records_list), rejected=0)

    def finish_batch(self, *, batch: OdsBatch, finished_at: UtcTimestamp) -> None:
        self.finished_batches.append(batch.batch_id)


class TestIngestToOds:
    """Tests for IngestToOds use case."""

    def _create_station(self, station_id: int) -> Station:
        return Station(
            id=StationId(station_id),
            dataset_id=DatasetId(f"{station_id}-dataset"),
            name=f"Station {station_id}",
            station_type=StationType.ISS,
        )

    def test_ingest_single_station(self) -> None:
        # Arrange
        clock = FakeClock(
            current_time=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        )
        weather = FakeWeatherRecords(
            records_by_station={
                42: [{"id": 1, "temp": 20.0}, {"id": 2, "temp": 21.0}]
            }
        )
        ods = FakeOdsRepository()

        uc = IngestToOds(weather=weather, ods=ods, clock=clock)

        station = self._create_station(42)
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
        )

        # Act
        report = uc.execute(stations=[station], window=window)

        # Assert
        assert report.station_count == 1
        assert report.total_inserted == 2
        assert report.total_rejected == 0
        assert len(ods.batches) == 1
        assert len(ods.records) == 1
        assert len(ods.finished_batches) == 1

    def test_ingest_multiple_stations(self) -> None:
        # Arrange
        clock = FakeClock(
            current_time=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        )
        weather = FakeWeatherRecords(
            records_by_station={
                42: [{"id": 1, "temp": 20.0}],
                43: [{"id": 2, "temp": 21.0}, {"id": 3, "temp": 22.0}],
            }
        )
        ods = FakeOdsRepository()

        uc = IngestToOds(weather=weather, ods=ods, clock=clock)

        stations = [self._create_station(42), self._create_station(43)]
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
        )

        # Act
        report = uc.execute(stations=stations, window=window)

        # Assert
        assert report.station_count == 2
        assert report.total_inserted == 3
        assert report.total_rejected == 0
        assert len(ods.records) == 2

    def test_ingest_no_stations(self) -> None:
        # Arrange
        clock = FakeClock(
            current_time=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        )
        weather = FakeWeatherRecords(records_by_station={})
        ods = FakeOdsRepository()

        uc = IngestToOds(weather=weather, ods=ods, clock=clock)

        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
        )

        # Act
        report = uc.execute(stations=[], window=window)

        # Assert
        assert report.station_count == 0
        assert report.total_inserted == 0
        assert report.total_rejected == 0

    def test_ingest_station_with_no_records(self) -> None:
        # Arrange
        clock = FakeClock(
            current_time=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        )
        weather = FakeWeatherRecords(records_by_station={42: []})
        ods = FakeOdsRepository()

        uc = IngestToOds(weather=weather, ods=ods, clock=clock)

        station = self._create_station(42)
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
        )

        # Act
        report = uc.execute(stations=[station], window=window)

        # Assert
        assert report.station_count == 1
        assert report.total_inserted == 0
        assert report.total_rejected == 0

    def test_ingest_creates_batch_with_correct_metadata(self) -> None:
        # Arrange
        clock = FakeClock(
            current_time=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        )
        weather = FakeWeatherRecords(records_by_station={42: [{"id": 1}]})
        ods = FakeOdsRepository()

        uc = IngestToOds(weather=weather, ods=ods, clock=clock)

        station = self._create_station(42)
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
        )

        # Act
        uc.execute(stations=[station], window=window)

        # Assert
        assert len(ods.batches) == 1
        batch = ods.batches[0]
        assert batch.station_count == 1
        assert batch.window == window
        assert batch.started_at == clock.current_time

    def test_ingest_finishes_batch(self) -> None:
        # Arrange
        clock = FakeClock(
            current_time=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        )
        weather = FakeWeatherRecords(records_by_station={42: [{"id": 1}]})
        ods = FakeOdsRepository()

        uc = IngestToOds(weather=weather, ods=ods, clock=clock)

        station = self._create_station(42)
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
        )

        # Act
        report = uc.execute(stations=[station], window=window)

        # Assert
        assert len(ods.finished_batches) == 1
        assert ods.finished_batches[0] == report.batch_id
