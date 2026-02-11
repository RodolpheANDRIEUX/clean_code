from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import requests

from src.domain.model.station import Station
from src.domain.model.time import TimeWindow


@dataclass(frozen=True, slots=True)
class ToulouseRecordsConfig:
    base_url: str = "https://data.toulouse-metropole.fr"
    timeout_s: float = 15.0
    page_size: int = 100
    max_records_per_station: int = 5_000  # sécurité
    timestamp_field: str = "heure_utc"


class ToulouseWeatherRecordsAdapter:
    """
    Explore API v2.1:
    GET /api/explore/v2.1/catalog/datasets/{dataset_id}/records

    V1: pagination simple par offset/limit, filtre sur heure_utc si présent.
    """

    def __init__(self, cfg: ToulouseRecordsConfig, session: Optional[requests.Session] = None) -> None:
        self._cfg = cfg
        self._session = session or requests.Session()

    def fetch_records(self, station: Station, window: TimeWindow) -> list[dict]:
        dataset_id = station.dataset_id.value
        url = f"{self._cfg.base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}/records"

        where = self._build_where(window)

        out: list[dict] = []
        offset = 0

        while True:
            remaining = self._cfg.max_records_per_station - len(out)
            if remaining <= 0:
                break

            limit = min(self._cfg.page_size, remaining)

            params: dict[str, Any] = {"limit": limit, "offset": offset, "where": where}

            try:
                data = self._get_json(url, params=params)
            except requests.HTTPError as e:
                resp = getattr(e, "response", None)
                if resp is not None and resp.status_code == 400:
                    return []
                raise

            results = data.get("results", [])
            if not results:
                break

            for r in results:
                if isinstance(r, dict):
                    out.append(r)

            if len(results) < limit:
                break

            offset += limit

        return out

    def _build_where(self, window: TimeWindow) -> str:
        """
        On filtre sur heure_utc si le champ existe (dans vos exemples il existe).
        Format ISO 8601 avec offset.
        """
        start = window.start.value.isoformat()
        end = window.end.value.isoformat()
        # ODS utilise une syntaxe SQL-like. V1 simple.
        field = self._cfg.timestamp_field
        return f"{field} >= date'{start}' AND {field} < date'{end}'"

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        resp = self._session.get(url, params=params, timeout=self._cfg.timeout_s)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Réponse JSON inattendue (dict attendu).")
        return data
