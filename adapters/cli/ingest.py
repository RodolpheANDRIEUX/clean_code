from __future__ import annotations

import typer

from domain.model.time import TimeWindow, UtcTimestamp
from infrastructure.wiring import build_get_selected_stations, build_ingest_to_ods, build_clock

app = typer.Typer(no_args_is_help=True)


@app.command("latest")
def latest(
        since: str = typer.Option(..., help="ISO8601 UTC (ex: 2025-12-01T00:00:00+00:00)"),
        until: str = typer.Option("", help="ISO8601 UTC. Vide = maintenant."),
        sqlite_path: str = typer.Option("data/app.sqlite", help="Chemin SQLite"),
        max_datasets: int = typer.Option(50, help="Limite le nombre de datasets catalog analysés"),
        whitelist: str = typer.Option(
            "",
            help="IDs station séparés par des virgules, ex: '1,3,5'",
        ),
) -> None:

    start = UtcTimestamp.from_iso8601(since)
    end = UtcTimestamp.from_iso8601(until) if until.strip() else None

    # 1) Use case : sélection des stations
    stations_uc = build_get_selected_stations(max_datasets=max_datasets)
    stations = stations_uc.execute()

    # 2) Filtrage CLI (choix utilisateur)
    if whitelist.strip():
        wl = {int(x.strip()) for x in whitelist.split(",")}
        stations = [s for s in stations if s.id.value in wl]

    if not stations:
        print("Aucune station après filtrage.")
        raise typer.Exit(code=0)

    # 3) Use case : ingestion
    ingest_uc = build_ingest_to_ods(sqlite_path=sqlite_path)

    clock = build_clock()
    if end is None:
        end = clock.now_utc()

    window = TimeWindow(start=start, end=end)

    report = ingest_uc.execute(stations=stations, window=window)

    print(f"batch_id={report.batch_id}")
    print(f"stations={report.station_count}")
    print(f"inserted={report.total_inserted} rejected={report.total_rejected}")
    print(f"window={report.window}")
