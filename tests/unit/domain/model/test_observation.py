"""Tests for Observation domain model."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from src.domain.model.observation import Observation, Measures, ObservationSeries
from src.domain.model.identifiers import StationId, RecordId
from src.domain.model.time import UtcTimestamp, TimeWindow
from src.domain.model.measures import TemperatureC, HumidityPct, WindVector, WindSpeed, WindDirectionDeg
from src.domain.model.quality import QualityStatus, QualityFlag


class TestMeasures:
    """Tests for Measures composite value object."""

    def test_valid_measures_full(self) -> None:
        measures = Measures(
            temperature=TemperatureC(20.5),
            humidity=HumidityPct(75.0),
        )
        assert measures.temperature.value == 20.5
        assert measures.humidity.value == 75.0

    def test_measures_all_optional(self) -> None:
        measures = Measures()
        assert measures.temperature is None
        assert measures.humidity is None
        assert measures.pressure is None
        assert measures.rain is None
        assert measures.rain_intensity_max is None
        assert measures.wind is None

    def test_measures_immutable(self) -> None:
        measures = Measures(temperature=TemperatureC(20.5))
        with pytest.raises(AttributeError):
            measures.temperature = TemperatureC(25.0)  # type: ignore


class TestObservation:
    """Tests for Observation entity."""

    def test_valid_observation(self) -> None:
        station_id = StationId(42)
        timestamp = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        measures = Measures(temperature=TemperatureC(20.5))
        
        obs = Observation(
            station_id=station_id,
            timestamp_utc=timestamp,
            measures=measures,
        )
        
        assert obs.station_id == station_id
        assert obs.timestamp_utc == timestamp
        assert obs.measures == measures
        assert obs.quality.is_ok()

    def test_observation_with_quality(self) -> None:
        station_id = StationId(42)
        timestamp = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        measures = Measures(temperature=TemperatureC(20.5))
        quality = QualityStatus.from_flags([QualityFlag.FUTURE_TIMESTAMP])
        
        obs = Observation(
            station_id=station_id,
            timestamp_utc=timestamp,
            measures=measures,
            quality=quality,
        )
        
        assert obs.quality.has(QualityFlag.FUTURE_TIMESTAMP)

    def test_observation_with_record_id(self) -> None:
        station_id = StationId(42)
        timestamp = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        measures = Measures(temperature=TemperatureC(20.5))
        record_id = RecordId("rec-123")
        
        obs = Observation(
            station_id=station_id,
            timestamp_utc=timestamp,
            measures=measures,
            raw_record_id=record_id,
        )
        
        assert obs.raw_record_id == record_id

    def test_observation_immutable(self) -> None:
        station_id = StationId(42)
        timestamp = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        measures = Measures(temperature=TemperatureC(20.5))
        
        obs = Observation(
            station_id=station_id,
            timestamp_utc=timestamp,
            measures=measures,
        )
        
        with pytest.raises(AttributeError):
            obs.station_id = StationId(43)  # type: ignore

    def test_observation_requires_measures(self) -> None:
        station_id = StationId(42)
        timestamp = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        
        with pytest.raises(ValueError, match="measures ne peut pas être None"):
            Observation(
                station_id=station_id,
                timestamp_utc=timestamp,
                measures=None,  # type: ignore
            )

    def test_observation_requires_at_least_one_measure(self) -> None:
        station_id = StationId(42)
        timestamp = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        measures = Measures()  # All None
        
        with pytest.raises(ValueError, match="au moins une mesure"):
            Observation(
                station_id=station_id,
                timestamp_utc=timestamp,
                measures=measures,
            )


class TestObservationSeries:
    """Tests for ObservationSeries aggregate."""

    def _create_observation(self, station_id: int, hour: int, temp: float) -> Observation:
        return Observation(
            station_id=StationId(station_id),
            timestamp_utc=UtcTimestamp(datetime(2025, 12, 1, hour, 0, 0, tzinfo=timezone.utc)),
            measures=Measures(temperature=TemperatureC(temp)),
        )

    def test_valid_observation_series(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        obs2 = self._create_observation(42, 10, 21.0)
        
        series = ObservationSeries(
            station_id=station_id,
            points=(obs1, obs2),
        )
        
        assert series.station_id == station_id
        assert len(series.points) == 2

    def test_observation_series_immutable(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        
        series = ObservationSeries(
            station_id=station_id,
            points=(obs1,),
        )
        
        with pytest.raises(AttributeError):
            series.station_id = StationId(43)  # type: ignore

    def test_observation_series_requires_consistent_station_id(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        obs2 = self._create_observation(43, 10, 21.0)  # Different station!
        
        with pytest.raises(ValueError, match="station_id incohérent"):
            ObservationSeries(
                station_id=station_id,
                points=(obs1, obs2),
            )

    def test_observation_series_requires_sorted_timestamps(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 10, 21.0)
        obs2 = self._create_observation(42, 9, 20.0)  # Out of order!
        
        with pytest.raises(ValueError, match="triés par timestamp"):
            ObservationSeries(
                station_id=station_id,
                points=(obs1, obs2),
            )

    def test_observation_series_requires_unique_timestamps(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        obs2 = self._create_observation(42, 9, 21.0)  # Same timestamp!
        
        with pytest.raises(ValueError, match="timestamps dupliqués"):
            ObservationSeries(
                station_id=station_id,
                points=(obs1, obs2),
            )

    def test_from_points_sorts_automatically(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 10, 21.0)
        obs2 = self._create_observation(42, 9, 20.0)
        obs3 = self._create_observation(42, 11, 22.0)
        
        series = ObservationSeries.from_points(
            station_id=station_id,
            points=[obs1, obs2, obs3],
        )
        
        assert len(series.points) == 3
        assert series.points[0].timestamp_utc.value.hour == 9
        assert series.points[1].timestamp_utc.value.hour == 10
        assert series.points[2].timestamp_utc.value.hour == 11

    def test_latest_with_points(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        obs2 = self._create_observation(42, 10, 21.0)
        
        series = ObservationSeries(
            station_id=station_id,
            points=(obs1, obs2),
        )
        
        latest = series.latest()
        assert latest is not None
        assert latest.timestamp_utc.value.hour == 10

    def test_latest_empty_series(self) -> None:
        station_id = StationId(42)
        series = ObservationSeries(
            station_id=station_id,
            points=(),
        )
        
        assert series.latest() is None

    def test_slice_within_window(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        obs2 = self._create_observation(42, 10, 21.0)
        obs3 = self._create_observation(42, 11, 22.0)
        
        series = ObservationSeries(
            station_id=station_id,
            points=(obs1, obs2, obs3),
        )
        
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 9, 30, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 10, 30, 0, tzinfo=timezone.utc)),
        )
        
        sliced = series.slice(window)
        assert len(sliced.points) == 1
        assert sliced.points[0].timestamp_utc.value.hour == 10

    def test_slice_empty_result(self) -> None:
        station_id = StationId(42)
        obs1 = self._create_observation(42, 9, 20.0)
        
        series = ObservationSeries(
            station_id=station_id,
            points=(obs1,),
        )
        
        window = TimeWindow(
            start=UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc)),
            end=UtcTimestamp(datetime(2025, 12, 1, 11, 0, 0, tzinfo=timezone.utc)),
        )
        
        sliced = series.slice(window)
        assert len(sliced.points) == 0
