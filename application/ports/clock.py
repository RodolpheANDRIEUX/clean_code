from __future__ import annotations
from typing import Protocol
from domain.model.time import UtcTimestamp


class ClockPort(Protocol):
    def now_utc(self) -> UtcTimestamp:
        ...
