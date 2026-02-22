"""Data Profiler — `src/data_tests/profiler.py`

Analyse le contenu de `ods_weather_raw` et produit un rapport de data
profiling complet (structurel, qualité, statistique, temporel).

Dépendances : stdlib uniquement (sqlite3, json, statistics, collections).
Aucune dépendance externe ajoutée au projet.

Usage::

    from src.data_tests.profiler import DataProfiler
    from src.infrastructure.db import connect_sqlite, SqliteConfig

    con = connect_sqlite(SqliteConfig())
    report = DataProfiler(con).run()
    print(report.to_text())
"""
from __future__ import annotations

import json
import sqlite3
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constantes — champs numériques extraits du payload JSON
# ---------------------------------------------------------------------------

NUMERIC_FIELDS: dict[str, dict[str, Any]] = {
    "temperature_en_degre_c": {"unit": "°C",    "min_bound": -100.0, "max_bound": 80.0},
    "humidite":               {"unit": "%",     "min_bound": 0.0,    "max_bound": 110.0},
    "pression":               {"unit": "Pa",    "min_bound": 80_000, "max_bound": 110_000},
    "pluie":                  {"unit": "mm",    "min_bound": 0.0,    "max_bound": 500.0},
    "pluie_intensite_max":    {"unit": "mm/h",  "min_bound": 0.0,    "max_bound": 1_000.0},
    "force_moyenne_du_vecteur_vent": {"unit": "m/s?", "min_bound": 0.0, "max_bound": 80.0},
    "force_rafale_max":       {"unit": "m/s?",  "min_bound": 0.0,    "max_bound": 80.0},
    "direction_du_vecteur_de_vent_max_en_degres": {"unit": "°", "min_bound": 0.0, "max_bound": 360.0},
}

CATEGORICAL_FIELDS: list[str] = ["type_de_station"]


# ---------------------------------------------------------------------------
# Result dataclasses (plain data, no logic)
# ---------------------------------------------------------------------------

@dataclass
class NumericFieldProfile:
    field_name: str
    unit: str
    total: int
    null_count: int
    min_val: Optional[float]
    max_val: Optional[float]
    mean: Optional[float]
    median: Optional[float]
    stdev: Optional[float]
    p25: Optional[float]
    p75: Optional[float]
    out_of_bounds: int        # valeurs hors bornes métier
    min_bound: float
    max_bound: float

    @property
    def null_pct(self) -> float:
        return (self.null_count / self.total * 100) if self.total else 0.0

    @property
    def out_of_bounds_pct(self) -> float:
        non_null = self.total - self.null_count
        return (self.out_of_bounds / non_null * 100) if non_null else 0.0


@dataclass
class TemporalProfile:
    total_rows: int
    ts_null_count: int
    ts_min: Optional[str]
    ts_max: Optional[str]
    station_row_counts: dict[int, int]      # station_id → nb rows
    gaps_per_station: dict[int, int]        # station_id → nb gaps > 30 min
    duplicate_keys: int                     # (station_id, ts_utc) doublons


@dataclass
class BatchProfile:
    total_batches: int
    finished_batches: int
    unfinished_batches: int
    last_batch_at: Optional[str]


@dataclass
class DataProfile:
    generated_at: str
    total_rows: int
    numeric_fields: list[NumericFieldProfile]
    categorical: dict[str, Counter]          # field → value counts
    temporal: TemporalProfile
    batches: BatchProfile

    # ------------------------------------------------------------------ #
    # Text rendering                                                       #
    # ------------------------------------------------------------------ #

    def to_text(self) -> str:
        lines: list[str] = []
        _h = lines.append

        _h("=" * 72)
        _h("  DATA PROFILE -- ods_weather_raw")
        _h(f"  Genere le : {self.generated_at}")
        _h("=" * 72)
        _h(f"\n[Vue d'ensemble] {self.total_rows:,} enregistrements\n")

        # --- Batches ---
        b = self.batches
        _h("-- Batches d'ingestion" + "-" * 50)
        _h(f"  Total         : {b.total_batches}")
        _h(f"  Termines      : {b.finished_batches}")
        _h(f"  Non termines  : {b.unfinished_batches}")
        _h(f"  Dernier batch : {b.last_batch_at or 'N/A'}")

        # --- Temporel ---
        t = self.temporal
        _h("\n-- Couverture temporelle" + "-" * 48)
        _h(f"  Timestamp NULL : {t.ts_null_count:,}  ({t.ts_null_count/self.total_rows*100:.1f}%)")
        _h(f"  Periode        : {t.ts_min}  -->  {t.ts_max}")
        _h(f"  Doublons (station+ts) : {t.duplicate_keys:,}")
        _h(f"\n  Lignes par station :")
        for sid, cnt in sorted(t.station_row_counts.items()):
            gaps = t.gaps_per_station.get(sid, 0)
            _h(f"    station {sid:>3} : {cnt:>7,} rows | gaps > 30 min : {gaps}")

        # --- Champs numeriques ---
        _h("\n-- Profil statistique des champs numeriques" + "-" * 29)
        for nf in self.numeric_fields:
            _h(f"\n  [{nf.field_name}]  ({nf.unit})")
            _h(f"    NULL      : {nf.null_count:,} / {nf.total:,}  ({nf.null_pct:.1f}%)")
            if nf.min_val is not None:
                _h(f"    Min/Max   : {nf.min_val:.2f}  /  {nf.max_val:.2f}")
                _h(f"    Moyenne   : {nf.mean:.2f}   Mediane : {nf.median:.2f}   std : {nf.stdev:.2f}")
                _h(f"    Q25/Q75   : {nf.p25:.2f}  /  {nf.p75:.2f}")
                flag = "[!!]" if nf.out_of_bounds > 0 else "[OK]"
                _h(f"    Hors bornes [{nf.min_bound}, {nf.max_bound}] : "
                   f"{flag} {nf.out_of_bounds:,}  ({nf.out_of_bounds_pct:.2f}%)")
            else:
                _h("    Aucune valeur non-nulle.")

        # --- Categoriel ---
        if self.categorical:
            _h("\n-- Champs categoriel" + "-" * 52)
            for fname, counts in self.categorical.items():
                _h(f"\n  [{fname}]")
                for val, cnt in counts.most_common():
                    _h(f"    {str(val):>20} : {cnt:,}")

        _h("\n" + "=" * 72)
        return "\n".join(lines)

    def to_html(self) -> str:
        """Génère un rapport HTML autonome avec style embarqué."""
        text = self.to_text()
        b = self.batches
        t = self.temporal

        # Build HTML sections
        numeric_rows = ""
        for nf in self.numeric_fields:
            oob_class = "danger" if nf.out_of_bounds > 0 else "ok"
            null_class = "warn" if nf.null_pct > 20 else "ok"
            if nf.min_val is not None:
                numeric_rows += f"""
                <tr>
                    <td><strong>{nf.field_name}</strong><br/><small>{nf.unit}</small></td>
                    <td class="{null_class}">{nf.null_count:,}<br/><small>({nf.null_pct:.1f}%)</small></td>
                    <td>{nf.min_val:.2f}</td>
                    <td>{nf.max_val:.2f}</td>
                    <td>{nf.mean:.2f}</td>
                    <td>{nf.median:.2f}</td>
                    <td>{nf.stdev:.2f}</td>
                    <td>{nf.p25:.2f} / {nf.p75:.2f}</td>
                    <td class="{oob_class}">{nf.out_of_bounds:,}<br/><small>({nf.out_of_bounds_pct:.2f}%)</small></td>
                </tr>"""
            else:
                numeric_rows += f"""
                <tr>
                    <td><strong>{nf.field_name}</strong></td>
                    <td colspan="8"><em>Toutes les valeurs sont NULL</em></td>
                </tr>"""

        station_rows = ""
        for sid, cnt in sorted(t.station_row_counts.items()):
            gaps = t.gaps_per_station.get(sid, 0)
            gap_class = "warn" if gaps > 10 else "ok"
            station_rows += f"""
            <tr>
                <td>Station {sid}</td>
                <td>{cnt:,}</td>
                <td class="{gap_class}">{gaps}</td>
            </tr>"""

        cat_sections = ""
        for fname, counts in self.categorical.items():
            rows_cat = "".join(
                f"<tr><td>{v}</td><td>{c:,}</td></tr>"
                for v, c in counts.most_common()
            )
            cat_sections += f"""
            <h3>{fname}</h3>
            <table><thead><tr><th>Valeur</th><th>Occurrences</th></tr></thead>
            <tbody>{rows_cat}</tbody></table>"""

        return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Data Profile — ods_weather_raw</title>
<style>
  :root {{
    --bg: #0f1117; --surface: #1a1d27; --border: #2e3250;
    --text: #e2e8f0; --muted: #8892b0; --accent: #64ffda;
    --ok: #4ade80; --warn: #facc15; --danger: #f87171;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Inter', 'Segoe UI', sans-serif; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; color: var(--accent); margin-bottom: .25rem; }}
  .subtitle {{ color: var(--muted); font-size: .9rem; margin-bottom: 2rem; }}
  h2 {{ font-size: 1.1rem; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: .4rem; margin: 2rem 0 1rem; }}
  h3 {{ font-size: .95rem; color: var(--muted); margin: 1rem 0 .5rem; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .kpi {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.1rem 1.3rem; }}
  .kpi .label {{ font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }}
  .kpi .value {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); margin-top: .25rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .85rem; }}
  th {{ background: var(--surface); color: var(--muted); padding: .6rem .8rem; text-align: left; border-bottom: 2px solid var(--border); }}
  td {{ padding: .55rem .8rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tr:hover td {{ background: var(--surface); }}
  .ok {{ color: var(--ok); }}
  .warn {{ color: var(--warn); }}
  .danger {{ color: var(--danger); }}
  small {{ font-size: .75rem; color: var(--muted); }}
  pre {{ background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
         padding: 1rem; font-size: .78rem; overflow-x: auto; color: var(--muted); white-space: pre-wrap; }}
</style>
</head>
<body>
<h1>📊 Data Profile</h1>
<p class="subtitle">Table : <code>ods_weather_raw</code> &nbsp;·&nbsp; Généré le {self.generated_at}</p>

<h2>Vue d'ensemble</h2>
<div class="kpi-grid">
  <div class="kpi"><div class="label">Total rows</div><div class="value">{self.total_rows:,}</div></div>
  <div class="kpi"><div class="label">Stations</div><div class="value">{len(t.station_row_counts)}</div></div>
  <div class="kpi"><div class="label">Batches</div><div class="value">{b.total_batches}</div></div>
  <div class="kpi"><div class="label">Doublons (station+ts)</div><div class="value {'danger' if t.duplicate_keys else 'ok'}">{t.duplicate_keys:,}</div></div>
  <div class="kpi"><div class="label">Période début</div><div class="value" style="font-size:.9rem">{t.ts_min or 'N/A'}</div></div>
  <div class="kpi"><div class="label">Période fin</div><div class="value" style="font-size:.9rem">{t.ts_max or 'N/A'}</div></div>
</div>

<h2>Couverture par station</h2>
<table>
  <thead><tr><th>Station</th><th>Lignes</th><th>Gaps &gt; 30 min</th></tr></thead>
  <tbody>{station_rows}</tbody>
</table>

<h2>Profil statistique — Champs numériques</h2>
<table>
  <thead><tr>
    <th>Champ</th><th>Nulls</th><th>Min</th><th>Max</th>
    <th>Moyenne</th><th>Médiane</th><th>σ</th><th>Q25/Q75</th><th>Hors bornes</th>
  </tr></thead>
  <tbody>{numeric_rows}</tbody>
</table>

<h2>Champs catégoriels</h2>
{cat_sections}

<h2>Rapport texte complet</h2>
<pre>{text}</pre>

</body></html>"""


# ---------------------------------------------------------------------------
# Core profiler
# ---------------------------------------------------------------------------

class DataProfiler:
    """Reads `ods_weather_raw` and produces a ``DataProfile``.

    Args:
        con: Open SQLite connection (read-only access is enough).
        table: Table name to profile. Default: ``ods_weather_raw``.
        batch_table: Batch tracking table. Default: ``ods_ingest_batch``.
        sample_size: Max rows to load for statistical analysis.
            ``None`` = all rows (may be slow on large datasets).
    """

    TABLE_RAW = "ods_weather_raw"
    TABLE_BATCH = "ods_ingest_batch"

    def __init__(
        self,
        con: sqlite3.Connection,
        *,
        table: str = TABLE_RAW,
        batch_table: str = TABLE_BATCH,
        sample_size: Optional[int] = None,
    ) -> None:
        self._con = con
        self._table = table
        self._batch_table = batch_table
        self._sample_size = sample_size

    # ------------------------------------------------------------------ #
    # Public                                                               #
    # ------------------------------------------------------------------ #

    def run(self) -> DataProfile:
        rows = self._load_rows()
        payloads = [json.loads(r["payload_json"]) for r in rows]

        return DataProfile(
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            total_rows=self._count_total(),
            numeric_fields=self._profile_numeric(payloads),
            categorical=self._profile_categorical(payloads),
            temporal=self._profile_temporal(rows),
            batches=self._profile_batches(),
        )

    # ------------------------------------------------------------------ #
    # Private — data loading                                               #
    # ------------------------------------------------------------------ #

    def _count_total(self) -> int:
        row = self._con.execute(f"SELECT COUNT(*) AS c FROM {self._table}").fetchone()
        return row["c"]

    def _load_rows(self) -> list[sqlite3.Row]:
        limit = f"LIMIT {self._sample_size}" if self._sample_size else ""
        return self._con.execute(
            f"SELECT station_id, ts_utc, payload_json FROM {self._table} {limit}"
        ).fetchall()

    # ------------------------------------------------------------------ #
    # Private — numeric                                                    #
    # ------------------------------------------------------------------ #

    def _profile_numeric(self, payloads: list[dict]) -> list[NumericFieldProfile]:
        results: list[NumericFieldProfile] = []
        n_total = len(payloads)

        for field_name, meta in NUMERIC_FIELDS.items():
            values: list[float] = []
            null_count = 0
            out_of_bounds = 0

            for payload in payloads:
                raw = payload.get(field_name)
                if raw is None:
                    null_count += 1
                    continue
                try:
                    v = float(raw)
                except (ValueError, TypeError):
                    null_count += 1
                    continue
                values.append(v)
                if v < meta["min_bound"] or v > meta["max_bound"]:
                    out_of_bounds += 1

            if values:
                sorted_vals = sorted(values)
                n = len(sorted_vals)
                p25 = sorted_vals[int(n * 0.25)]
                p75 = sorted_vals[int(n * 0.75)]
                results.append(NumericFieldProfile(
                    field_name=field_name,
                    unit=meta["unit"],
                    total=n_total,
                    null_count=null_count,
                    min_val=sorted_vals[0],
                    max_val=sorted_vals[-1],
                    mean=statistics.mean(values),
                    median=statistics.median(values),
                    stdev=statistics.stdev(values) if len(values) > 1 else 0.0,
                    p25=p25,
                    p75=p75,
                    out_of_bounds=out_of_bounds,
                    min_bound=meta["min_bound"],
                    max_bound=meta["max_bound"],
                ))
            else:
                results.append(NumericFieldProfile(
                    field_name=field_name, unit=meta["unit"],
                    total=n_total, null_count=null_count,
                    min_val=None, max_val=None, mean=None,
                    median=None, stdev=None, p25=None, p75=None,
                    out_of_bounds=0,
                    min_bound=meta["min_bound"], max_bound=meta["max_bound"],
                ))
        return results

    # ------------------------------------------------------------------ #
    # Private — categorical                                                #
    # ------------------------------------------------------------------ #

    def _profile_categorical(self, payloads: list[dict]) -> dict[str, Counter]:
        result: dict[str, Counter] = {}
        for fname in CATEGORICAL_FIELDS:
            result[fname] = Counter(p.get(fname) for p in payloads)
        return result

    # ------------------------------------------------------------------ #
    # Private — temporal                                                   #
    # ------------------------------------------------------------------ #

    def _profile_temporal(self, rows: list[sqlite3.Row]) -> TemporalProfile:
        ts_null = 0
        ts_values: list[str] = []
        station_timestamps: defaultdict[int, list[str]] = defaultdict(list)
        seen_keys: set[tuple] = set()
        duplicate_keys = 0

        for row in rows:
            ts = row["ts_utc"]
            sid = row["station_id"]
            key = (sid, ts)
            if key in seen_keys:
                duplicate_keys += 1
            seen_keys.add(key)

            if ts is None:
                ts_null += 1
            else:
                ts_values.append(ts)
                station_timestamps[sid].append(ts)

        station_row_counts: dict[int, int] = {
            sid: len(tss) for sid, tss in station_timestamps.items()
        }
        gaps_per_station = self._compute_gaps(station_timestamps)

        return TemporalProfile(
            total_rows=len(rows),
            ts_null_count=ts_null,
            ts_min=min(ts_values) if ts_values else None,
            ts_max=max(ts_values) if ts_values else None,
            station_row_counts=station_row_counts,
            gaps_per_station=gaps_per_station,
            duplicate_keys=duplicate_keys,
        )

    def _compute_gaps(
        self, station_timestamps: defaultdict[int, list[str]]
    ) -> dict[int, int]:
        """Count gaps > 30 min between consecutive timestamps per station."""
        gaps: dict[int, int] = {}
        threshold_seconds = 30 * 60  # 30 minutes

        for sid, tss in station_timestamps.items():
            sorted_tss = sorted(tss)
            gap_count = 0
            for i in range(1, len(sorted_tss)):
                try:
                    t1 = datetime.fromisoformat(sorted_tss[i - 1])
                    t2 = datetime.fromisoformat(sorted_tss[i])
                    diff = abs((t2 - t1).total_seconds())
                    if diff > threshold_seconds:
                        gap_count += 1
                except Exception:
                    pass
            gaps[sid] = gap_count

        return gaps

    # ------------------------------------------------------------------ #
    # Private — batches                                                    #
    # ------------------------------------------------------------------ #

    def _profile_batches(self) -> BatchProfile:
        try:
            rows = self._con.execute(
                f"SELECT finished_at_utc, started_at_utc FROM {self._batch_table}"
            ).fetchall()
        except Exception:
            return BatchProfile(0, 0, 0, None)

        total = len(rows)
        finished = sum(1 for r in rows if r["finished_at_utc"] is not None)
        last_at = max((r["started_at_utc"] for r in rows), default=None)

        return BatchProfile(
            total_batches=total,
            finished_batches=finished,
            unfinished_batches=total - finished,
            last_batch_at=last_at,
        )
