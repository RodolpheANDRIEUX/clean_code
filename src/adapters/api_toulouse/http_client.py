"""Shared HTTP helper for Toulouse API adapters.

Extracts the duplicated ``_get_json`` logic (DRY).
"""
from __future__ import annotations

from typing import Any

import requests


def get_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    """Execute a GET request and return the parsed JSON dict.

    Raises:
        requests.HTTPError: On non-2xx responses.
        ValueError: When the response is not a JSON dict.
    """
    resp = session.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("Reponse JSON inattendue (dict attendu).")
    return data
