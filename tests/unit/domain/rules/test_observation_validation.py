"""Tests for observation validation domain rules."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from src.domain.model.observation import Observation, Measures
from src.domain.model.identifiers import StationId
from src.domain.model.time import UtcTimestamp
from src.domain.model.measures import TemperatureC, RainMm, RainIntensityMmH
from src.domain.model.quality import QualityFlag
from src.domain.rules.observation_validation import ObservationValidator, ValidationConfig


class TestValidationConfig:
    """Tests for ValidationConfig."""

    def test_default_config(self) -> None:
        config = ValidationConfig()
        assert config.max_future_skew == timedelta(minutes=5)

    def test_custom_config(self) -> None:
        config = ValidationConfig(max_future_skew=timedelta(minutes=10))
        assert config.max_future_skew == timedelta(minutes=10)

    def test_config_immutable(self) -> None:
        config = ValidationConfig()
        with pytest.raises(AttributeError):
            config.max_future_skew = timedelta(minutes=10)  # type: ignore


class TestObservationValidator:
    """Tests for ObservationValidator."""

    def _create_observation(
        self,
        hour: int,
        temp: float | None = 20.0,
        rain: float | None = None,
        rain_intensity: float | None = None,
    ) -> Observation:
        measures_dict = {}
        if temp is not None:
            measures_dict["temperature"] = TemperatureC(temp)
        if rain is not None:
            measures_dict["rain"] = RainMm(rain)
        if rain_intensity is not None:
            measures_dict["rain_intensity_max"] = RainIntensityMmH(rain_intensity)
        
        return Observation(
            station_id=StationId(42),
            timestamp_utc=UtcTimestamp(datetime(2025, 12, 1, hour, 0, 0, tzinfo=timezone.utc)),
            measures=Measures(**measures_dict),
        )

    def test_validate_ok_observation(self) -> None:
        config = ValidationConfig()
        validator = ObservationValidator(config)
        
        obs = self._create_observation(hour=9)
        now = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert status.is_ok()

    def test_validate_future_timestamp_beyond_tolerance(self) -> None:
        config = ValidationConfig(max_future_skew=timedelta(minutes=5))
        validator = ObservationValidator(config)
        
        # Observation at 10:00
        obs = self._create_observation(hour=10)
        # Now is 9:00 -> observation is 1 hour in future (beyond 5 min tolerance)
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert not status.is_ok()
        assert status.has(QualityFlag.FUTURE_TIMESTAMP)

    def test_validate_future_timestamp_within_tolerance(self) -> None:
        config = ValidationConfig(max_future_skew=timedelta(minutes=5))
        validator = ObservationValidator(config)
        
        # Observation at 9:03
        obs = self._create_observation(hour=9)
        obs = Observation(
            station_id=StationId(42),
            timestamp_utc=UtcTimestamp(datetime(2025, 12, 1, 9, 3, 0, tzinfo=timezone.utc)),
            measures=Measures(temperature=TemperatureC(20.0)),
        )
        # Now is 9:00 -> observation is 3 min in future (within 5 min tolerance)
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert status.is_ok()

    def test_validate_past_timestamp(self) -> None:
        config = ValidationConfig()
        validator = ObservationValidator(config)
        
        # Observation at 8:00
        obs = self._create_observation(hour=8)
        # Now is 10:00 -> observation is in the past (OK)
        now = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert status.is_ok()

    def test_validate_rain_intensity_without_rain(self) -> None:
        config = ValidationConfig()
        validator = ObservationValidator(config)
        
        # Rain = 0 but intensity > 0 (suspicious)
        obs = self._create_observation(hour=9, rain=0.0, rain_intensity=10.0)
        now = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        # Should flag as UNKNOWN (or SUSPICIOUS if you add that flag)
        assert not status.is_ok()
        assert status.has(QualityFlag.UNKNOWN)

    def test_validate_rain_with_intensity(self) -> None:
        config = ValidationConfig()
        validator = ObservationValidator(config)
        
        # Rain > 0 and intensity > 0 (consistent)
        obs = self._create_observation(hour=9, rain=5.0, rain_intensity=10.0)
        now = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert status.is_ok()

    def test_validate_no_rain_no_intensity(self) -> None:
        config = ValidationConfig()
        validator = ObservationValidator(config)
        
        # Rain = 0 and intensity = 0 (consistent)
        obs = self._create_observation(hour=9, rain=0.0, rain_intensity=0.0)
        now = UtcTimestamp(datetime(2025, 12, 1, 10, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert status.is_ok()

    def test_validate_custom_tolerance(self) -> None:
        config = ValidationConfig(max_future_skew=timedelta(minutes=10))
        validator = ObservationValidator(config)
        
        # Observation at 9:08
        obs = Observation(
            station_id=StationId(42),
            timestamp_utc=UtcTimestamp(datetime(2025, 12, 1, 9, 8, 0, tzinfo=timezone.utc)),
            measures=Measures(temperature=TemperatureC(20.0)),
        )
        # Now is 9:00 -> observation is 8 min in future (within 10 min tolerance)
        now = UtcTimestamp(datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc))
        
        status = validator.validate(obs, now=now)
        assert status.is_ok()
