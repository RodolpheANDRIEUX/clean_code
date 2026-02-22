# Weather ETL - Guide de verification

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Pre-requis : **Python 3.12+**

---

## 1. Execution sans erreur

```bash
python -m src.adapters.cli.main stations list-selected
python -m src.adapters.cli.main data stations
python -m src.adapters.cli.main data latest
python -m src.adapters.cli.main data show 3
```

---

## 2. Recuperer la meteo en ligne

```bash
python -m src.adapters.cli.main ingest latest --since "2025-12-01T07:00:00+00:00" --until "2025-12-01T10:00:00+00:00"
```

Affiche `batch_id`, `stations`, `inserted`, `rejected`.

---

## 3. Afficher la meteo

```bash
python -m src.adapters.cli.main data latest       # derniere mesure par station
python -m src.adapters.cli.main data show 3        # historique station 3
python -m src.adapters.cli.main data show 3 --n 50 # 50 derniers releves
```

Colonnes affichees : Temp, Humid, Press, Pluie, Vent, Rafale.

---

## 4. Tests unitaires

```bash
python -m pytest tests/ -v
```

**247 tests**, tous passent.

---

## 5. PyLint

```bash
python -m pylint src/ --disable=C0114,C0115,C0116
```

Score : **9.54/10**

---

## 6. Principes SOLID, KISS, DRY, YAGNI

| Principe | Ou verifier |
|---|---|
| **S** - Single Responsibility | Chaque fichier = 1 classe/responsabilite. Ex: `src/application/use_cases/ingest_to_ods.py` |
| **O** - Open/Closed | `src/adapters/weather_decorator.py` : on ajoute du logging sans modifier l'adapter |
| **L** - Liskov | `LoggingWeatherRecordsDecorator` remplace `ToulouseWeatherRecordsAdapter` sans casser |
| **I** - Interface Segregation | Protocols minimalistes : `ClockPort` (1 methode), `WeatherRecordsPort` (1 methode) |
| **D** - Dependency Inversion | `IngestToOds` depend des Protocols, pas des classes concretes |
| **KISS** | Pas de meta-programmation, classes courtes, profiler en stdlib pure |
| **DRY** | `_get_json()` factorise dans `src/adapters/api_toulouse/http_client.py` |
| **YAGNI** | Pas de code mort. Structures de donnees = exercice pedagogique |

---

## 7. Structure du projet

```
src/
  domain/              <- modele metier pur, 0 dependance externe
    model/             <- entites, value objects (Station, Observation...)
    rules/             <- regles metier (StationSelector, ObservationValidator)
    structures/        <- structures de donnees (LinkedList, Queue, HashTable, Tree, Graph)
  application/         <- use cases + ports (interfaces)
    ports/             <- Protocols : ClockPort, WeatherRecordsPort, Command
    use_cases/         <- IngestToOds, GetSelectedStations
  adapters/            <- implementations concretes
    api_toulouse/      <- adapter HTTP (station_catalog, weather_records, http_client)
    cli/               <- interface utilisateur Typer (stations, ingest, ods, data)
    persistence/       <- SQLite (SqliteOdsRepository)
    weather_decorator.py <- GoF Decorator
  infrastructure/      <- wiring, config, DB
  data_tests/          <- DataProfiler
tests/
  unit/domain/         <- tests unitaires
```

Tous les dossiers ont un `__init__.py`.

---

## 8. Structures de donnees

| Structure | Fichier | Tests |
|---|---|---|
| **Liste chainee** | `src/domain/structures/linked_list.py` | `tests/unit/domain/structures/test_linked_list.py` |
| **File (Queue)** | `src/domain/structures/queue.py` | `tests/unit/domain/structures/test_queue.py` |
| **Dictionnaire (HashTable)** | `src/domain/structures/hash_table.py` | `tests/unit/domain/structures/test_hash_table.py` |
| Arbre N-aire | `src/domain/structures/tree.py` | `tests/unit/domain/structures/test_tree.py` |
| Graphe | `src/domain/structures/graph.py` | `tests/unit/domain/structures/test_graph.py` |

Toutes heritent de `BaseStructure[T]` (`base_structure.py`).
Le nom de chaque structure est explicite dans le nom de classe et dans les docstrings.

---

## 9. Design Patterns (3)

Detail complet : [design_patterns.md](design_patterns.md)

| Pattern | Categorie | Fichiers cles |
|---|---|---|
| **Factory Method** | Creation | `QualityStatus.ok()`, `StationType.from_raw()` |
| **Command** | Comportement | `src/application/ports/command.py` + use cases + `src/adapters/cli/stations.py` |
| **Decorator** | Structure | `src/adapters/weather_decorator.py` + `src/infrastructure/wiring.py` |

---

## 10. Documentation

| Type | Emplacement |
|---|---|
| Data Profiling | `python scripts/run_data_profile.py` → rapport `scripts/data_profile.html` |
| Docstrings + typage | Sur toutes les classes du domaine et structures |
| Conventions | `conventions.md` |
| PEP8 | `snake_case` fonctions, `PascalCase` classes — verifie par pylint |

---

## 11. Data Profiling

```bash
python scripts/run_data_profile.py
```

Options : `--text-only`, `--output path.html`, `--sample 5000`

Couvre : nulls, bornes metier, min/max/moyenne/mediane/ecart-type, gaps temporels, doublons.
