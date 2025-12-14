from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Iterable


class QualityFlag(str, Enum):
    """
    Flags métier. Vous pourrez en ajouter sans casser le modèle.
    """
    MISSING_FIELD = "MISSING_FIELD"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    FUTURE_TIMESTAMP = "FUTURE_TIMESTAMP"
    DUPLICATE = "DUPLICATE"
    PARSE_ERROR = "PARSE_ERROR"
    INCONSISTENT_TIME = "INCONSISTENT_TIME"
    UNKNOWN_STATION = "UNKNOWN_STATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class QualityStatus:
    flags: FrozenSet[QualityFlag] = frozenset()

    @classmethod
    def ok(cls) -> "QualityStatus":
        return cls(frozenset())

    @classmethod
    def from_flags(cls, flags: Iterable[QualityFlag]) -> "QualityStatus":
        return cls(frozenset(flags))

    def is_ok(self) -> bool:
        return len(self.flags) == 0

    def has(self, flag: QualityFlag) -> bool:
        return flag in self.flags

    def add(self, flag: QualityFlag) -> "QualityStatus":
        return QualityStatus(self.flags | frozenset({flag}))

    def merge(self, other: "QualityStatus") -> "QualityStatus":
        return QualityStatus(self.flags | other.flags)
