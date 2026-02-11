from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .identifiers import StationId, DatasetId


class StationType(str, Enum):
    """
    Typologie métier.
    Vous avez un exemple 'ISS'. On garde une catégorie OTHER pour ne pas casser.
    """
    ISS = "ISS"
    OTHER = "OTHER"

    @classmethod
    def from_raw(cls, raw: str | None) -> "StationType":
        if raw is None:
            return cls.OTHER
        s = str(raw).strip().upper()
        if s == "ISS":
            return cls.ISS
        return cls.OTHER


@dataclass(frozen=True, slots=True)
class GeoPoint:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError("Latitude invalide.")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError("Longitude invalide.")


@dataclass(frozen=True, slots=True)
class Station:
    """
    Entité station côté métier.
    - dataset_id : vous permet de relier à un dataset ODS concret
    - is_active : utile pour filtrer vos stations retenues
    """
    id: StationId
    dataset_id: DatasetId
    name: str
    station_type: StationType
    is_active: bool = True

    commune: Optional[str] = None
    geopoint: Optional[GeoPoint] = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Station.name ne peut pas être vide.")
