from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Optional

from domain.model.station import Station, StationId, StationType


@dataclass(frozen=True, slots=True)
class StationSelectionPolicy:
    """
    Politique de sélection des stations.
    V1: simple, explicite, testable.
    """
    allowed_types: FrozenSet[StationType] = frozenset({StationType.ISS})
    allow_inactive: bool = False

    # Optionnel: forcer un sous-ensemble (utile en MVP)
    whitelist: Optional[FrozenSet[StationId]] = None

    # Optionnel: exclure explicitement
    blacklist: FrozenSet[StationId] = frozenset()

    def accepts(self, station: Station) -> bool:
        if station.id in self.blacklist:
            return False

        if self.whitelist is not None and station.id not in self.whitelist:
            return False

        if station.station_type not in self.allowed_types:
            return False

        if (not self.allow_inactive) and (not station.is_active):
            return False

        return True


class StationSelector:
    """
    Service métier: applique une policy et renvoie une liste stable (triée).
    """
    def __init__(self, policy: StationSelectionPolicy) -> None:
        self._policy = policy

    def select(self, candidates: Iterable[Station]) -> list[Station]:
        selected = [s for s in candidates if self._policy.accepts(s)]
        selected.sort(key=lambda s: s.id.value)
        return selected
