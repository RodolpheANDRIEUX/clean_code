from __future__ import annotations

from datetime import datetime, timezone
from domain.model.time import UtcTimestamp

from application.use_cases.get_selected_stations import GetSelectedStations
from application.use_cases.ingest_to_ods import IngestToOds
from domain.model import StationId

from domain.rules.station_selection import StationSelectionPolicy
from domain.model.station import StationType
from domain.model.time import UtcTimestamp

from adapters.api_toulouse.station_catalog import ToulouseApiConfig, ToulouseStationCatalogAdapter
from adapters.api_toulouse.weather_records import ToulouseRecordsConfig, ToulouseWeatherRecordsAdapter
from adapters.persistence.sqlite_ods_repo import SqliteOdsRepository
from infrastructure.db import SqliteConfig, connect_sqlite


class SystemClock:
    def now_utc(self) -> UtcTimestamp:
        return UtcTimestamp(datetime.now(timezone.utc))


def build_clock() -> SystemClock:
    return SystemClock()


def build_get_selected_stations(
        *,
        max_datasets: int = 50,
        allow_other_types: bool = False,
        whitelist: list[int] | None = None,
) -> GetSelectedStations:
    catalog = ToulouseStationCatalogAdapter(
        cfg=ToulouseApiConfig(max_datasets=max_datasets)
    )

    allowed = {StationType.ISS}
    if allow_other_types:
        allowed.add(StationType.OTHER)

    wl = None
    if whitelist:
        wl = frozenset(StationId(i) for i in whitelist)

    policy = StationSelectionPolicy(
        allowed_types=frozenset(allowed),
        allow_inactive=False,
        whitelist=wl,
    )

    return GetSelectedStations(catalog=catalog, policy=policy)


def build_ingest_to_ods(*, sqlite_path: str = "data/app.sqlite") -> IngestToOds:
    con = connect_sqlite(SqliteConfig(path=sqlite_path))
    ods = SqliteOdsRepository(con)
    weather = ToulouseWeatherRecordsAdapter(cfg=ToulouseRecordsConfig())
    clock = SystemClock()
    return IngestToOds(weather=weather, ods=ods, clock=clock)
