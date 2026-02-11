from __future__ import annotations

from typing import Protocol

from domain.model.station import Station


class StationCatalogPort(Protocol):
    """
    Port (contrat) : une source capable de fournir des stations candidates.
    L'implémentation concrète sera un adapter (fake, HTTP, DB, etc.).
    """
    def list_candidate_stations(self) -> list[Station]:
        ...
