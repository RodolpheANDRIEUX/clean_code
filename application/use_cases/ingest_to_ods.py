from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from application.ports.clock import ClockPort
from application.ports.ods import OdsRepositoryPort, OdsBatch
from application.ports.weather import WeatherRecordsPort
from domain.model.station import Station
from domain.model.time import TimeWindow, UtcTimestamp


@dataclass(frozen=True, slots=True)
class IngestReport:
    batch_id: str
    station_count: int
    total_inserted: int
    total_rejected: int
    window: TimeWindow


class IngestToOds:
    """
    Use case ETL V1:
    - pour chaque station sélectionnée, fetch des records bruts sur une fenêtre
    - append-only dans l'ODS
    """
    def __init__(
            self,
            *,
            weather: WeatherRecordsPort,
            ods: OdsRepositoryPort,
            clock: ClockPort,
    ) -> None:
        self._weather = weather
        self._ods = ods
        self._clock = clock

    def execute(self, *, stations: Iterable[Station], window: TimeWindow) -> IngestReport:
        stations_list = list(stations)
        started_at = self._clock.now_utc()

        batch = self._ods.start_batch(window=window, station_count=len(stations_list), started_at=started_at)

        total_inserted = 0
        total_rejected = 0

        for st in stations_list:
            raw = self._weather.fetch_records(st, window)
            res = self._ods.append_station_records(batch=batch, station=st, records=raw)
            total_inserted += res.inserted
            total_rejected += res.rejected

        finished_at = self._clock.now_utc()
        self._ods.finish_batch(batch=batch, finished_at=finished_at)

        return IngestReport(
            batch_id=batch.batch_id,
            station_count=len(stations_list),
            total_inserted=total_inserted,
            total_rejected=total_rejected,
            window=window,
        )
