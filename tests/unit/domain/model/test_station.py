"""Tests for Station domain model."""
from __future__ import annotations

import pytest

from src.domain.model.station import Station, StationType, GeoPoint, StationId, DatasetId


class TestStationType:
    """Tests for StationType enum."""

    def test_from_raw_iss(self) -> None:
        assert StationType.from_raw("ISS") == StationType.ISS
        assert StationType.from_raw("iss") == StationType.ISS
        assert StationType.from_raw("  ISS  ") == StationType.ISS

    def test_from_raw_other(self) -> None:
        assert StationType.from_raw("UNKNOWN") == StationType.OTHER
        assert StationType.from_raw("") == StationType.OTHER
        assert StationType.from_raw(None) == StationType.OTHER


class TestGeoPoint:
    """Tests for GeoPoint value object."""

    def test_valid_geopoint(self) -> None:
        gp = GeoPoint(latitude=43.6047, longitude=1.4442)
        assert gp.latitude == 43.6047
        assert gp.longitude == 1.4442

    def test_geopoint_immutable(self) -> None:
        gp = GeoPoint(latitude=43.6047, longitude=1.4442)
        with pytest.raises(AttributeError):
            gp.latitude = 50.0  # type: ignore

    def test_invalid_latitude_too_low(self) -> None:
        with pytest.raises(ValueError, match="Latitude invalide"):
            GeoPoint(latitude=-91.0, longitude=1.4442)

    def test_invalid_latitude_too_high(self) -> None:
        with pytest.raises(ValueError, match="Latitude invalide"):
            GeoPoint(latitude=91.0, longitude=1.4442)

    def test_invalid_longitude_too_low(self) -> None:
        with pytest.raises(ValueError, match="Longitude invalide"):
            GeoPoint(latitude=43.6047, longitude=-181.0)

    def test_invalid_longitude_too_high(self) -> None:
        with pytest.raises(ValueError, match="Longitude invalide"):
            GeoPoint(latitude=43.6047, longitude=181.0)

    def test_boundary_values(self) -> None:
        # Test exact boundaries
        GeoPoint(latitude=-90.0, longitude=-180.0)
        GeoPoint(latitude=90.0, longitude=180.0)


class TestStation:
    """Tests for Station entity."""

    def test_valid_station(self) -> None:
        station = Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse"),
            name="Station Toulouse",
            station_type=StationType.ISS,
            is_active=True,
        )
        assert station.id.value == 42
        assert station.dataset_id.value == "42-station-meteo-toulouse"
        assert station.name == "Station Toulouse"
        assert station.station_type == StationType.ISS
        assert station.is_active is True

    def test_station_with_geopoint(self) -> None:
        gp = GeoPoint(latitude=43.6047, longitude=1.4442)
        station = Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse"),
            name="Station Toulouse",
            station_type=StationType.ISS,
            geopoint=gp,
        )
        assert station.geopoint == gp

    def test_station_with_commune(self) -> None:
        station = Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse"),
            name="Station Toulouse",
            station_type=StationType.ISS,
            commune="Toulouse",
        )
        assert station.commune == "Toulouse"

    def test_station_immutable(self) -> None:
        station = Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse"),
            name="Station Toulouse",
            station_type=StationType.ISS,
        )
        with pytest.raises(AttributeError):
            station.name = "New Name"  # type: ignore

    def test_invalid_station_empty_name(self) -> None:
        with pytest.raises(ValueError, match="name ne peut pas être vide"):
            Station(
                id=StationId(42),
                dataset_id=DatasetId("42-station-meteo-toulouse"),
                name="",
                station_type=StationType.ISS,
            )

    def test_invalid_station_whitespace_name(self) -> None:
        with pytest.raises(ValueError, match="name ne peut pas être vide"):
            Station(
                id=StationId(42),
                dataset_id=DatasetId("42-station-meteo-toulouse"),
                name="   ",
                station_type=StationType.ISS,
            )

    def test_station_default_is_active(self) -> None:
        station = Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse"),
            name="Station Toulouse",
            station_type=StationType.ISS,
        )
        assert station.is_active is True

    def test_station_inactive(self) -> None:
        station = Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse"),
            name="Station Toulouse",
            station_type=StationType.ISS,
            is_active=False,
        )
        assert station.is_active is False
