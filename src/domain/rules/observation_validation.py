from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from src.domain.model.observation import Observation
from src.domain.model.quality import QualityFlag, QualityStatus
from src.domain.model.time import UtcTimestamp


@dataclass(frozen=True, slots=True)
class ValidationConfig:
    """
    Paramètres métier (pas techniques).
    Ils peuvent venir de la config application, mais la logique reste ici.
    """
    max_future_skew: timedelta = timedelta(minutes=5)


class ObservationValidator:
    """
    Valide une Observation déjà construite.
    Ne fait aucun I/O.
    """
    def __init__(self, config: ValidationConfig) -> None:
        self._config = config

    def validate(self, obs: Observation, *, now: UtcTimestamp) -> QualityStatus:
        status = QualityStatus.ok()

        # 1) Timestamp futur
        if obs.timestamp_utc.value > (now.value + self._config.max_future_skew):
            status = status.add(QualityFlag.FUTURE_TIMESTAMP)

        # 2) Cohérence pluie/intensité (exemple)
        # (optionnel) si intensité max > 0 mais pluie == 0, ce n'est pas forcément faux,
        # mais peut être suspect selon votre métier.
        if obs.measures.rain is not None and obs.measures.rain.value == 0.0:
            if (
                obs.measures.rain_intensity_max is not None
                and obs.measures.rain_intensity_max.value > 0.0
            ):
                status = status.add(QualityFlag.UNKNOWN)  # remplacez par un flag "SUSPICIOUS"

        # 3) Au moins une mesure (déjà garanti dans Observation.__post_init__)
        # Ici on pourrait ajouter des validations inter-champs si besoin.

        return status
