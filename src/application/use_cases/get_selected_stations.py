from __future__ import annotations

from src.domain.model.station import Station
from src.domain.rules.station_selection import StationSelectionPolicy, StationSelector

from src.application.ports.stations import StationCatalogPort


class GetSelectedStations:
    """
    Use case : récupérer les stations candidates (via un port),
    appliquer la politique de sélection (domain/rules),
    renvoyer la liste des stations retenues.
    """

    def __init__(self, catalog: StationCatalogPort, policy: StationSelectionPolicy) -> None:
        self._catalog = catalog
        self._selector = StationSelector(policy)

    def execute(self) -> list[Station]:
        candidates = self._catalog.list_candidate_stations()
        return self._selector.select(candidates)
