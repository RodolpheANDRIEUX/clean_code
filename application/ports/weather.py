from __future__ import annotations
from typing import Any, Mapping, TypeAlias, Protocol
from domain.model.station import Station
from domain.model.time import TimeWindow

RawRecord: TypeAlias = Mapping[str, Any]


class WeatherRecordsPort(Protocol):
    def fetch_records(self, station: Station, window: TimeWindow) -> list[RawRecord]:
        ...
