# Design Patterns

Trois patterns GoF implémentés dans le projet.

---

## 🏭 Création — Factory Method

**Objectif :** encapsuler la création d'un objet derrière une méthode nommée.

```python
# src/domain/model/quality.py
QualityStatus.ok()                          # crée un statut "sans flag"
QualityStatus.from_flags([OUT_OF_RANGE])    # crée un statut avec flags

# src/domain/model/station.py
StationType.from_raw("ISS")   # parse + valide + retourne l'enum
```

Le client ne fait jamais `QualityStatus(frozenset())` à la main — la factory le fait pour lui.

---

## ⚡ Comportement — Command

**Objectif :** encapsuler une requête en objet, avec une interface unique `execute()`.

```python
# src/application/ports/command.py
class Command(Protocol[T]):
    def execute(self) -> T: ...
```

| ConcreteCommand | Ce qu'il fait |
|---|---|
| `GetSelectedStations` | liste + filtre les stations via l'API |
| `IngestToOds` | fetch les records et les persiste en SQLite |

Le CLI (Invoker) appelle `.execute()` sans jamais importer le concret.

---

## 🎁 Structure — Decorator

**Objectif :** ajouter du comportement à un objet sans modifier sa classe.

```
WeatherRecordsPort              ← interface (Component)
  ├── ToulouseWeatherRecordsAdapter  ← implémentation réelle
  └── LoggingWeatherRecordsDecorator ← wrapper qui loggue les appels
           │
           └── délègue à ToulouseWeatherRecordsAdapter
```

```python
# src/infrastructure/wiring.py
weather = LoggingWeatherRecordsDecorator(
    ToulouseWeatherRecordsAdapter(cfg=...)
)
# IngestToOds ne sait pas qu'il est décoré — même interface
```

Le Decorator s'empile : demain on peut ajouter un `RetryDecorator` par-dessus sans toucher à rien.
