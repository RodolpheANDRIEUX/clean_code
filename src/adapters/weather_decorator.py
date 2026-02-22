"""GoF Decorator pattern — sur WeatherRecordsPort.

Le Decorator permet d'ajouter du comportement à un objet existant en conservant
la même interface, sans modifier la classe originale et sans que le client
(IngestToOds) sache si la dépendance est décorée ou non.

    Component hierarchy
    ───────────────────
    WeatherRecordsPort          ← Component (Protocol existant)
      ├── ToulouseWeatherRecordsAdapter  ← ConcreteComponent (existant)
      ├── WeatherRecordsDecorator        ← Decorator abstrait (ce fichier)
      │     └── LoggingWeatherRecordsDecorator  ← ConcreteDecorator (ce fichier)
      └── ... (futurs décorateurs : retry, cache, circuit-breaker...)

Pourquoi le Decorator ici ?
    - L'architecture hexagonale interdit de polluer le domaine ou les use cases
      avec du logging/retry.
    - Le Decorator respecte l'OCP : on ajoute du comportement sans modifier
      ToulouseWeatherRecordsAdapter.
    - Entièrement transparent pour IngestToOds : il reçoit un WeatherRecordsPort,
      qu'il soit décoré ou non.

Wiring (wiring.py) :
    weather = LoggingWeatherRecordsDecorator(ToulouseWeatherRecordsAdapter(cfg))
    uc = IngestToOds(weather=weather, ods=ods, clock=clock)  # ← rien à changer
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from src.application.ports.weather import RawRecord, WeatherRecordsPort
from src.domain.model.station import Station
from src.domain.model.time import TimeWindow

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Decorator abstrait — GoF Decorator base class
# ---------------------------------------------------------------------------

class WeatherRecordsDecorator(ABC):
    """Decorator abstrait : wrappe un WeatherRecordsPort.

    Toute sous-classe hérite de la même interface que le Component.
    Elle délègue par défaut et les ConcreteDecorators ajoutent leur comportement
    avant/après l'appel délégué.
    """

    def __init__(self, wrapped: WeatherRecordsPort) -> None:
        self._wrapped = wrapped

    @abstractmethod
    def fetch_records(self, station: Station, window: TimeWindow) -> list[RawRecord]:
        """Déléguer à _wrapped, en ajoutant du comportement."""


# ---------------------------------------------------------------------------
# ConcreteDecorator — ajoute du logging autour de fetch_records
# ---------------------------------------------------------------------------

class LoggingWeatherRecordsDecorator(WeatherRecordsDecorator):
    """Loggue chaque appel fetch_records (station, window, nb records retournés).

    Transparent pour IngestToOds : il reçoit un WeatherRecordsPort sans savoir
    que les appels sont journalisés.

    Usage::

        from src.adapters.weather_decorator import LoggingWeatherRecordsDecorator
        from src.adapters.api_toulouse.weather_records import ToulouseWeatherRecordsAdapter

        adapter   = ToulouseWeatherRecordsAdapter(cfg=ToulouseRecordsConfig())
        decorated = LoggingWeatherRecordsDecorator(adapter)  # même interface

        # IngestToOds ne voit pas la différence :
        uc = IngestToOds(weather=decorated, ods=ods, clock=clock)
    """

    def fetch_records(self, station: Station, window: TimeWindow) -> list[RawRecord]:
        logger.debug(
            "WeatherRecords.fetch_records | station=%s | window=%s-->%s",
            station.id,
            window.start.value.isoformat(),
            window.end.value.isoformat(),
        )

        records = self._wrapped.fetch_records(station, window)

        logger.debug(
            "WeatherRecords.fetch_records | station=%s | fetched=%d records",
            station.id,
            len(records),
        )
        return records
