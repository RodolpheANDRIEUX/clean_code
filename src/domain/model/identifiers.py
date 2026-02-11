from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StationId:
    """Identité métier d'une station (ex: 42)."""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError("StationId.value doit être un int.")
        if self.value <= 0:
            raise ValueError("StationId.value doit être strictement positif.")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class DatasetId:
    """
    Identifiant Opendatasoft du dataset (slug).
    Ex: '42-station-meteo-toulouse-parc-compans-cafarelli'
    """
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("DatasetId.value doit être une str.")
        v = self.value.strip()
        if not v:
            raise ValueError("DatasetId.value ne peut pas être vide.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RecordId:
    """
    Identifiant brut d'enregistrement côté source (ex: champ 'data' dans votre JSON).
    Utile pour traçabilité/déduplication si vous le souhaitez.
    """
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("RecordId.value doit être une str.")
        v = self.value.strip()
        if not v:
            raise ValueError("RecordId.value ne peut pas être vide.")

    def __str__(self) -> str:
        return self.value
