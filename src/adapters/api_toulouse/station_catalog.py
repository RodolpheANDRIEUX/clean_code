from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import requests

from src.domain.model.identifiers import DatasetId, StationId
from src.domain.model.station import Station, StationType


@dataclass(frozen=True, slots=True)
class ToulouseApiConfig:
    base_url: str = "https://data.toulouse-metropole.fr"
    timeout_s: float = 10.0
    max_datasets: int = 50


class ToulouseStationCatalogAdapter:
    """
    Implémente StationCatalogPort via l'API Opendatasoft Explore v2.1.

    Stratégie V1:
    - Lister les datasets météo modifiés en 2025 via /catalog/datasets (refine)
    - Pour chaque dataset, lire 1 record via /catalog/datasets/{id}/records?limit=1
      et utiliser ce record pour déduire station_id et type_de_station.
    """

    def __init__(self, cfg: ToulouseApiConfig, session: Optional[requests.Session] = None) -> None:
        self._cfg = cfg
        self._session = session or requests.Session()

    def list_candidate_stations(self) -> list[Station]:
        datasets = self._list_meteo_datasets_modified_2025(limit=self._cfg.max_datasets)

        stations: list[Station] = []
        seen_station_ids: set[int] = set()

        for ds in datasets:
            dataset_id = DatasetId(ds["dataset_id"])
            title = ds.get("title") or dataset_id.value

            sample = self._fetch_one_record(dataset_id.value)
            if sample is None:
                # dataset vide ou inaccessible -> on ignore en V1
                continue

            station_id_int = self._extract_station_id(sample)
            if station_id_int is None:
                continue

            if station_id_int in seen_station_ids:
                # plusieurs datasets peuvent référencer la même station; on garde le 1er
                continue
            seen_station_ids.add(station_id_int)

            st_type = StationType.from_raw(sample.get("type_de_station"))

            stations.append(
                Station(
                    id=StationId(station_id_int),
                    dataset_id=dataset_id,
                    name=str(title),
                    station_type=st_type,
                    is_active=True,  # V1: pas de référentiel "active" => on suppose actif
                )
            )

        stations.sort(key=lambda s: s.id.value)
        return stations

    def _list_meteo_datasets_modified_2025(self, limit: int) -> list[dict[str, Any]]:
        url = f"{self._cfg.base_url}/api/explore/v2.1/catalog/datasets"
        params = {
            "refine": [
                "keyword:météo",
                "modified:2025",
            ],
            "limit": limit,
        }

        data = self._get_json(url, params=params)
        results = data.get("results", [])
        out: list[dict[str, Any]] = []

        for r in results:
            # Les champs exacts peuvent varier; on essaie plusieurs chemins.
            dataset_id = r.get("dataset_id") or r.get("dataset") or r.get("id")
            title = (
                    r.get("metas", {}).get("title")
                    or r.get("metas", {}).get("default", {}).get("title")
                    or r.get("title")
            )
            if dataset_id:
                out.append({"dataset_id": dataset_id, "title": title})

        return out

    def _fetch_one_record(self, dataset_id: str) -> Optional[dict[str, Any]]:
        url = f"{self._cfg.base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}/records"
        params = {"limit": 1}

        data = self._get_json(url, params=params)
        results = data.get("results", [])
        if not results:
            return None
        first = results[0]
        if not isinstance(first, dict):
            return None
        return first

    @staticmethod
    def _extract_station_id(record: dict[str, Any]) -> Optional[int]:
        """
        Votre exemple montre un champ 'id' numérique (42).
        """
        raw = record.get("id")
        if raw is None:
            return None
        try:
            v = int(raw)
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        resp = self._session.get(url, params=params, timeout=self._cfg.timeout_s)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Réponse JSON inattendue (dict attendu).")
        return data
