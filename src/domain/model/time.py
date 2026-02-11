from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta


@dataclass(frozen=True, slots=True)
class UtcTimestamp:
    """
    Timestamp métier : datetime timezone-aware, normalisé en UTC.
    """
    value: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.value, datetime):
            raise TypeError("UtcTimestamp.value doit être un datetime.")
        if self.value.tzinfo is None:
            raise ValueError("UtcTimestamp.value doit être timezone-aware.")
        # Normaliser en UTC (sans perdre l'instant)
        object.__setattr__(self, "value", self.value.astimezone(timezone.utc))

    @classmethod
    def from_iso8601(cls, iso: str) -> "UtcTimestamp":
        """
        Accepte des ISO8601 type '2025-12-01T09:00:00+00:00' ou '...Z'.
        """
        if not isinstance(iso, str) or not iso.strip():
            raise ValueError("ISO8601 invalide.")
        s = iso.strip()
        # Python ne parse pas 'Z' directement dans fromisoformat
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        return cls(dt)

    def is_in_future(self, *, now: "UtcTimestamp", tolerance: timedelta = timedelta(minutes=5)) -> bool:
        return self.value > (now.value + tolerance)

    def __str__(self) -> str:
        # ISO 8601 UTC avec offset explicite
        return self.value.isoformat()


@dataclass(frozen=True, slots=True)
class TimeWindow:
    start: UtcTimestamp
    end: UtcTimestamp

    def __post_init__(self) -> None:
        if self.start.value >= self.end.value:
            raise ValueError("TimeWindow: start doit être strictement < end.")

    def contains(self, ts: UtcTimestamp) -> bool:
        return self.start.value <= ts.value < self.end.value

    def duration(self) -> timedelta:
        return self.end.value - self.start.value

    def __str__(self) -> str:
        return f"[{self.start} → {self.end})"
