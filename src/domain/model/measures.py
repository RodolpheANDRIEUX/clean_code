from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class TemperatureC:
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("TemperatureC.value doit être numérique.")
        v = float(self.value)
        # bornes physiques très larges pour ne pas rejeter trop tôt
        if v < -100.0 or v > 80.0:
            raise ValueError(f"Température hors bornes plausibles: {v}°C")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True, slots=True)
class HumidityPct:
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("HumidityPct.value doit être numérique.")
        v = float(self.value)
        # tolérance large (capteurs parfois >100)
        if v < 0.0 or v > 110.0:
            raise ValueError(f"Humidité hors bornes plausibles: {v}%")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True, slots=True)
class PressurePa:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("PressurePa.value doit être numérique.")
        v = int(round(float(self.value)))
        # pression atmosphérique typique ~101325 Pa, bornes très larges
        if v < 80000 or v > 110000:
            raise ValueError(f"Pression hors bornes plausibles: {v} Pa")
        object.__setattr__(self, "value", v)

    def to_hpa(self) -> float:
        return self.value / 100.0


@dataclass(frozen=True, slots=True)
class RainMm:
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("RainMm.value doit être numérique.")
        v = float(self.value)
        if v < 0.0 or v > 500.0:
            raise ValueError(f"Pluie hors bornes plausibles: {v} mm")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True, slots=True)
class RainIntensityMmH:
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("RainIntensityMmH.value doit être numérique.")
        v = float(self.value)
        if v < 0.0 or v > 1000.0:
            raise ValueError(f"Intensité pluie hors bornes plausibles: {v} mm/h")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True, slots=True)
class WindSpeed:
    """Vitesse en m/s (choix V1)."""
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("WindSpeed.value doit être numérique.")
        v = float(self.value)
        if v < 0.0 or v > 80.0:
            raise ValueError(f"Vent hors bornes plausibles: {v} m/s")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True, slots=True)
class WindDirectionDeg:
    """
    Direction en degrés, 0..360 inclus (0/360 = Nord).
    """
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)):
            raise TypeError("WindDirectionDeg.value doit être numérique.")
        v = int(round(float(self.value)))
        if v < 0 or v > 360:
            raise ValueError(f"Direction vent invalide: {v}°")
        object.__setattr__(self, "value", v)


@dataclass(frozen=True, slots=True)
class WindVector:
    """
    Regroupe les infos de vent.
    - mean_speed / mean_direction : vent moyen
    - max_gust / max_direction : rafale max + direction associée
    """
    mean_speed: Optional[WindSpeed] = None
    mean_direction: Optional[WindDirectionDeg] = None
    max_gust: Optional[WindSpeed] = None
    max_direction: Optional[WindDirectionDeg] = None
