from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable

from .identifiers import StationId, RecordId
from .time import UtcTimestamp, TimeWindow
from .measures import (
    TemperatureC,
    HumidityPct,
    PressurePa,
    RainMm,
    RainIntensityMmH,
    WindVector,
    WindSpeed,
    WindDirectionDeg,
)
from .quality import QualityStatus


@dataclass(frozen=True, slots=True)
class Measures:
    """
    Mesures d'une observation.
    On met des Optional car le capteur peut ne pas fournir certains champs.
    """
    temperature: Optional[TemperatureC] = None
    humidity: Optional[HumidityPct] = None
    pressure: Optional[PressurePa] = None
    rain: Optional[RainMm] = None
    rain_intensity_max: Optional[RainIntensityMmH] = None
    wind: Optional[WindVector] = None


@dataclass(frozen=True, slots=True)
class Observation:
    station_id: StationId
    timestamp_utc: UtcTimestamp
    measures: Measures
    quality: QualityStatus = QualityStatus.ok()
    raw_record_id: Optional[RecordId] = None

    def __post_init__(self) -> None:
        # Invariant simple : au moins une mesure présente
        if self.measures is None:
            raise ValueError("Observation.measures ne peut pas être None.")
        if (
                self.measures.temperature is None
                and self.measures.humidity is None
                and self.measures.pressure is None
                and self.measures.rain is None
                and self.measures.rain_intensity_max is None
                and self.measures.wind is None
        ):
            raise ValueError("Observation doit contenir au moins une mesure.")


@dataclass(frozen=True, slots=True)
class ObservationSeries:
    """
    Série temporelle immuable pour une station.
    Invariants :
    - station_id unique
    - tri croissant par timestamp
    - unicité des timestamps
    """
    station_id: StationId
    points: tuple[Observation, ...]

    def __post_init__(self) -> None:
        if any(p.station_id != self.station_id for p in self.points):
            raise ValueError("ObservationSeries: station_id incohérent dans les points.")

        # Tri + unicité (on impose)
        ts = [p.timestamp_utc.value for p in self.points]
        if ts != sorted(ts):
            raise ValueError("ObservationSeries: points doivent être triés par timestamp.")
        if len(ts) != len(set(ts)):
            raise ValueError("ObservationSeries: timestamps dupliqués.")

    @classmethod
    def from_points(cls, station_id: StationId, points: Iterable[Observation]) -> "ObservationSeries":
        pts = list(points)
        pts.sort(key=lambda o: o.timestamp_utc.value)
        return cls(station_id=station_id, points=tuple(pts))

    def latest(self) -> Optional[Observation]:
        return self.points[-1] if self.points else None

    def slice(self, window: TimeWindow) -> "ObservationSeries":
        sliced = [p for p in self.points if window.contains(p.timestamp_utc)]
        return ObservationSeries.from_points(self.station_id, sliced)
