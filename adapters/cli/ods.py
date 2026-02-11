from __future__ import annotations

import typer
from infrastructure.db import SqliteConfig, connect_sqlite

app = typer.Typer(no_args_is_help=True)


@app.command("stats")
def stats(sqlite_path: str = typer.Option("data/app.sqlite")) -> None:
    con = connect_sqlite(SqliteConfig(path=sqlite_path))
    cur = con.cursor()

    total = cur.execute("SELECT COUNT(*) FROM ods_weather_raw").fetchone()[0]
    batches = cur.execute("SELECT COUNT(*) FROM ods_ingest_batch").fetchone()[0]
    last = cur.execute(
        "SELECT batch_id, started_at_utc, finished_at_utc, station_count FROM ods_ingest_batch ORDER BY started_at_utc DESC LIMIT 1"
    ).fetchone()

    print(f"rows={total}")
    print(f"batches={batches}")
    if last:
        print(f"last_batch={last[0]} started={last[1]} finished={last[2]} stations={last[3]}")


@app.command("sample")
def sample(
        n: int = typer.Option(5),
        sqlite_path: str = typer.Option("data/app.sqlite"),
) -> None:
    con = connect_sqlite(SqliteConfig(path=sqlite_path))
    cur = con.cursor()
    rows = cur.execute(
        "SELECT station_id, dataset_id, ts_utc, record_id FROM ods_weather_raw ORDER BY id DESC LIMIT ?",
        (n,),
    ).fetchall()

    for r in rows:
        print(f"station={r[0]}\tdataset={r[1]}\tts_utc={r[2]}\trecord_id={r[3]}")
