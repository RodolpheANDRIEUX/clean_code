"""GoF Command pattern — contrat commun pour tous les use cases.

Le GoF Command exige une interface que tous les ConcreteCommand implémentent,
permettant à l'Invoker (ici le CLI) de les traiter uniformément sans connaître
leur implémentation concrète.

    Component hierarchy
    ───────────────────
    Command[T]          ← interface (ce fichier)
      ├── IngestToOds   ← ConcreteCommand  (use_cases/ingest_to_ods.py)
      └── GetSelectedStations ← ConcreteCommand (use_cases/get_selected_stations.py)

    Invoker : src/adapters/cli/  (appelle .execute() sans importer le concret)
"""
from __future__ import annotations

from typing import Generic, Protocol, TypeVar

T = TypeVar("T", covariant=True)


class Command(Protocol[T]):
    """Interface commune à tous les use cases exécutables.

    Un Command encapsule une requête avec toutes ses dépendances.
    L'Invoker appelle uniquement ``execute()`` — il ne sait rien du reste.
    """

    def execute(self) -> T:
        """Exécute la commande et retourne son résultat."""
        ...
