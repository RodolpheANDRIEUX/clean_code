from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Iterable

from src.application.ports.ods import OdsRepositoryPort, OdsBatch, OdsAppendResult
from src.application.ports.weather import RawRecord
from src.domain.model.station import Station
from src.domain.model.time import TimeWindow, UtcTimestamp


@dataclass(frozen=True, slots=True)
class SqliteOdsConfig:
    # table names kept explicit
    table_batch: str = "ods_ingest_batch"
    table_raw: str = "ods_weather_raw"


class SqliteOdsRepository(OdsRepositoryPort):
    def __init__(self, con: sqlite3.Connection, cfg: SqliteOdsConfig = SqliteOdsConfig()) -> None:
        self._con = con
        self._cfg = cfg
        self._ensure_schema()

    def start_batch(self, *, window: TimeWindow, station_count: int, started_at: UtcTimestamp) -> OdsBatch:
        batch_id = uuid.uuid4().hex
        self._con.execute(
            f"""
            INSERT INTO {self._cfg.table_batch} (batch_id, started_at_utc, window_start_utc, window_end_utc, station_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (batch_id, started_at.value.isoformat(), window.start.value.isoformat(), window.end.value.isoformat(), station_count),
        )
        self._con.commit()
        return OdsBatch(batch_id=batch_id, started_at=started_at, window=window, station_count=station_count)

    def append_station_records(self, *, batch: OdsBatch, station: Station, records: Iterable[RawRecord]) -> OdsAppendResult:
        inserted = 0
        rejected = 0

        cur = self._con.cursor()

        for r in records:
            try:
                payload = json.dumps(r, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            except Exception:
                rejected += 1
                continue

            checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()

            # Essayons d'extraire ts + record_id, sinon NULL.
            ts_utc = r.get("heure_utc")
            record_id = r.get("data")  # votre exemple

            try:
                cur.execute(
                    f"""
                    INSERT OR IGNORE INTO {self._cfg.table_raw}
                    (batch_id, station_id, dataset_id, record_id, ts_utc, payload_json, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        batch.batch_id,
                        station.id.value,
                        station.dataset_id.value,
                        str(record_id) if record_id is not None else None,
                        str(ts_utc) if ts_utc is not None else None,
                        payload,
                        checksum,
                    ),
                )
                # rowcount == 1 si inséré, 0 si ignoré (doublon unique)
                if cur.rowcount == 1:
                    inserted += 1
                else:
                    rejected += 1
            except Exception:
                rejected += 1

        self._con.commit()
        return OdsAppendResult(inserted=inserted, rejected=rejected)

    def finish_batch(self, *, batch: OdsBatch, finished_at: UtcTimestamp) -> None:
        self._con.execute(
            f"UPDATE {self._cfg.table_batch} SET finished_at_utc = ? WHERE batch_id = ?",
            (finished_at.value.isoformat(), batch.batch_id),
        )
        self._con.commit()

    def _ensure_schema(self) -> None:
        self._con.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._cfg.table_batch} (
                batch_id TEXT PRIMARY KEY,
                started_at_utc TEXT NOT NULL,
                finished_at_utc TEXT NULL,
                window_start_utc TEXT NOT NULL,
                window_end_utc TEXT NOT NULL,
                station_count INTEGER NOT NULL
            );
            """
        )
        self._con.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._cfg.table_raw} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                station_id INTEGER NOT NULL,
                dataset_id TEXT NOT NULL,
                record_id TEXT NULL,
                ts_utc TEXT NULL,
                payload_json TEXT NOT NULL,
                checksum TEXT NOT NULL,
                loaded_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                FOREIGN KEY(batch_id) REFERENCES {self._cfg.table_batch}(batch_id)
            );
            """
        )
        # Dédup V1: (dataset_id, record_id) si présent, sinon checksum
        self._con.execute(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_ods_raw_dataset_record
            ON {self._cfg.table_raw}(dataset_id, record_id)
            WHERE record_id IS NOT NULL;
            """
        )
        self._con.execute(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_ods_raw_checksum
            ON {self._cfg.table_raw}(checksum);
            """
        )
        self._con.commit()
