import logging
import os
import json
from typing import Mapping, Optional


class MinimalJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Ajout des champs que je pourrai eventuelement utiliser
        for key in ("event", "station_id", "rows", "duration_ms", "correlation_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(module_levels: Optional[Mapping[str, int]] = None) -> None:
    mode = os.getenv("APP_MODE", "PROD").upper()
    as_json = os.getenv("APP_LOG_JSON", "0") in ("1", "true", "TRUE")
    level = logging.DEBUG if mode == "DEV" else logging.INFO

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler()
    if as_json:
        formatter = MinimalJSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)

    if module_levels:
        for name, lvl in module_levels.items():
            logging.getLogger(name).setLevel(lvl)

# Exemple d'utilisation
# logger.info(
#     "Ingestion terminée",
#     extra={
#         "event": "ods_ingest",
#         "station_id": "S1",
#         "rows": 125
#     }
# )