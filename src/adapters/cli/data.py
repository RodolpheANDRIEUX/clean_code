"""CLI — consultation des données météo stockées.

Sous-commandes :
    data stations   → liste les stations présentes en base
    data show       → affiche les mesures d'une station
    data latest     → dernières mesures de chaque station
"""
from __future__ import annotations

import json
from typing import Any

import typer

from src.infrastructure.db import SqliteConfig, connect_sqlite

app = typer.Typer(no_args_is_help=True)

# ---------------------------------------------------------------------- #
# Helpers                                                                  #
# ---------------------------------------------------------------------- #

METEO_FIELDS = [
    ("temperature_en_degre_c", "Temp", "C"),
    ("humidite", "Humid", "%"),
    ("pression", "Press", "Pa"),
    ("pluie", "Pluie", "mm"),
    ("force_moyenne_du_vecteur_vent", "Vent", ""),
    ("force_rafale_max", "Rafale", ""),
]


def _format_value(raw: Any, unit: str) -> str:
    if raw is None:
        return "-"
    try:
        v = float(raw)
        return f"{v:.1f}{unit}"
    except (TypeError, ValueError):
        return str(raw)


def _parse_payload(payload_json: str) -> dict[str, Any]:
    try:
        return json.loads(payload_json)
    except Exception:
        return {}


# ---------------------------------------------------------------------- #
# Commands                                                                 #
# ---------------------------------------------------------------------- #

@app.command("stations")
def list_stations(
    sqlite_path: str = typer.Option("data/app.sqlite", help="Chemin SQLite"),
) -> None:
    """Liste les stations presentes en base avec leur nombre d'enregistrements."""
    con = connect_sqlite(SqliteConfig(path=sqlite_path))
    rows = con.execute(
        """
        SELECT station_id, dataset_id, COUNT(*) as cnt,
               MIN(ts_utc) as first_ts, MAX(ts_utc) as last_ts
        FROM ods_weather_raw
        GROUP BY station_id, dataset_id
        ORDER BY station_id
        """
    ).fetchall()

    if not rows:
        print("Aucune donnee en base.")
        raise typer.Exit(code=0)

    print(f"{'Station':>8}  {'Records':>8}  {'Debut':>26}  {'Fin':>26}  Dataset")
    print("-" * 100)
    for r in rows:
        print(
            f"{r['station_id']:>8}  {r['cnt']:>8}  "
            f"{r['first_ts'] or 'N/A':>26}  {r['last_ts'] or 'N/A':>26}  "
            f"{r['dataset_id']}"
        )


@app.command("show")
def show_station(
    station_id: int = typer.Argument(..., help="ID de la station"),
    n: int = typer.Option(20, help="Nombre de lignes"),
    sqlite_path: str = typer.Option("data/app.sqlite", help="Chemin SQLite"),
) -> None:
    """Affiche les mesures meteo d'une station (les N plus recentes)."""
    con = connect_sqlite(SqliteConfig(path=sqlite_path))
    rows = con.execute(
        """
        SELECT ts_utc, payload_json
        FROM ods_weather_raw
        WHERE station_id = ?
        ORDER BY ts_utc DESC
        LIMIT ?
        """,
        (station_id, n),
    ).fetchall()

    if not rows:
        print(f"Aucune donnee pour la station {station_id}.")
        raise typer.Exit(code=0)

    # Header
    header = f"{'Timestamp':>26}"
    for _, label, _ in METEO_FIELDS:
        header += f"  {label:>8}"
    print(header)
    print("-" * len(header))

    # Rows (reverse pour afficher du plus ancien au plus recent)
    for r in reversed(rows):
        p = _parse_payload(r["payload_json"])
        line = f"{r['ts_utc'] or 'N/A':>26}"
        for key, _, unit in METEO_FIELDS:
            line += f"  {_format_value(p.get(key), unit):>8}"
        print(line)

    print(f"\n({len(rows)} enregistrement(s) pour station {station_id})")


@app.command("latest")
def latest_all(
    sqlite_path: str = typer.Option("data/app.sqlite", help="Chemin SQLite"),
) -> None:
    """Affiche la derniere mesure de chaque station."""
    con = connect_sqlite(SqliteConfig(path=sqlite_path))

    stations = con.execute(
        "SELECT DISTINCT station_id FROM ods_weather_raw ORDER BY station_id"
    ).fetchall()

    if not stations:
        print("Aucune donnee en base.")
        raise typer.Exit(code=0)

    # Header
    header = f"{'Station':>8}  {'Timestamp':>26}"
    for _, label, _ in METEO_FIELDS:
        header += f"  {label:>8}"
    print(header)
    print("-" * len(header))

    for s in stations:
        sid = s["station_id"]
        row = con.execute(
            """
            SELECT ts_utc, payload_json
            FROM ods_weather_raw
            WHERE station_id = ?
            ORDER BY ts_utc DESC
            LIMIT 1
            """,
            (sid,),
        ).fetchone()

        if row:
            p = _parse_payload(row["payload_json"])
            line = f"{sid:>8}  {row['ts_utc'] or 'N/A':>26}"
            for key, _, unit in METEO_FIELDS:
                line += f"  {_format_value(p.get(key), unit):>8}"
            print(line)
