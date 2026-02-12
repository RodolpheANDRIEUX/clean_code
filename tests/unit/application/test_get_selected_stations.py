from __future__ import annotations

from dataclasses import dataclass

from src.application.use_cases.get_selected_stations import GetSelectedStations
from src.domain.model import StationId, DatasetId
from src.domain.model import Station, StationType
from src.domain.rules.station_selection import StationSelectionPolicy


@dataclass
class FakeCatalog:
    stations: list[Station]

    def list_candidate_stations(self) -> list[Station]:
        return self.stations


def test_get_selected_stations_filters_by_type_and_active() -> None:
    # Arrange
    candidates = [
        Station(
            id=StationId(42),
            dataset_id=DatasetId("42-station-meteo-toulouse-parc-compans-cafarelli"),
            name="Station 42",
            station_type=StationType.ISS,
            is_active=True,
        ),
        Station(
            id=StationId(43),
            dataset_id=DatasetId("43-station-meteo-toulouse-xxxx"),
            name="Station 43",
            station_type=StationType.OTHER,
            is_active=True,
        ),
        Station(
            id=StationId(44),
            dataset_id=DatasetId("44-station-meteo-toulouse-yyyy"),
            name="Station 44",
            station_type=StationType.ISS,
            is_active=False,
        ),
    ]

    catalog = FakeCatalog(candidates)
    policy = StationSelectionPolicy(
        allowed_types=frozenset({StationType.ISS}),
        allow_inactive=False,
    )

    uc = GetSelectedStations(catalog=catalog, policy=policy)

    # Act
    selected = uc.execute()

    # Assert
    assert [s.id.value for s in selected] == [42]
