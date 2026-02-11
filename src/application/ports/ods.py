from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Iterable
from src.application.ports.weather import RawRecord
from src.domain.model.station import Station
from src.domain.model.time import TimeWindow, UtcTimestamp


@dataclass(frozen=True, slots=True)
class OdsBatch:
    batch_id: str
    started_at: UtcTimestamp
    window: TimeWindow
    station_count: int


@dataclass(frozen=True, slots=True)
class OdsAppendResult:
    inserted: int
    rejected: int  # V1: doublons/records illisibles etc.


class OdsRepositoryPort(Protocol):
    def start_batch(self, *, window: TimeWindow, station_count: int, started_at: UtcTimestamp) -> OdsBatch:
        ...

    def append_station_records(self, *, batch: OdsBatch, station: Station,
                               records: Iterable[RawRecord]) -> OdsAppendResult:
        ...

    def finish_batch(self, *, batch: OdsBatch, finished_at: UtcTimestamp) -> None:
        ...
