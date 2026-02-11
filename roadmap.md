# Project Roadmap — ETL Météo (Hexagonal / Clean Code)


---

## Étape 0 — Fondations (FAIT)
**But : poser un cœur métier fiable**

- [x] Créer le `domain/`
    - Modèles métier (Station, Observation, Measures, Time, Quality…)
    - Invariants (immutabilité, bornes, cohérence)
- [x] Règles métier
    - `station_selection.py`
    - `observation_validation.py`
- [x] Comprendre le rôle du domain (vocabulaire + règles, pas de technique)

Livrable : objets métier sûrs + règles testables sans API ni DB.

---

## Étape 1 — Premier cas d’usage simple
**But : faire “vivre” le domain**

- [ ] Créer un premier use case :
    - `GetSelectedStations`
- [ ] Définir un premier port :
    - `StationCatalogPort`
- [ ] Tester le use case avec un fake (stations en mémoire)

Livrable : sélectionner les stations **sans HTTP**, **sans DB**.

---

## Étape 2 — Première entrée utilisateur (CLI)
**But : rendre le système concret**

- [ ] Créer une commande CLI :
    - `stations list-selected`
- [ ] Brancher le fake catalog au use case
- [ ] Affichage simple (print)

Livrable : une commande CLI fonctionnelle, entièrement testable.

---

## Étape 3 — Brancher la vraie API Toulouse
**But : remplacer le fake par le réel**

- [ ] Implémenter un adapter HTTP :
    - `ToulouseStationCatalogAdapter`
- [ ] Mapper API → objets `Station`
- [ ] Ne rien changer au domain ni au use case

Livrable : mêmes résultats, mais avec la vraie API.

---

## Étape 4 — Ingestion brute (ODS)
**But : commencer l’ETL**

- [ ] Use case `IngestToOds`
- [ ] Port `WeatherSourcePort`
- [ ] Port `OdsRepositoryPort`
- [ ] Adapter SQLite (append-only)
- [ ] Logs + rapport simple

Livrable : données brutes stockées proprement.

---

## Étape 5 — Qualité & transformation (DWH)
**But : données fiables et exploitables**

- [ ] Data tests ODS (schéma, bornes)
- [ ] Use case `BuildDwhFromOds`
- [ ] Normalisation + typage strict
- [ ] Data tests DWH

Livrable : DWH stable, prêt pour analyse/prévision.

---

## Étape 6 — Lecture & visualisation simple
**But : exploiter les données**

- [ ] Use case `GetObservations`
- [ ] CLI `show current`
- [ ] CLI `quality report`

Livrable : inspection simple des données.

---

## Étape 7 — Prévision (baseline)
**But : ajouter une capacité avancée sans casser l’existant**

- [ ] Port `ForecastPort`
- [ ] Adapter Prophet
- [ ] Use case `RunForecast`
- [ ] CLI `forecast run`

Livrable : prévisions propres, découplées de la techno.

---

## Étape 8 — Évolutions (R1)
**But : prouver la modularité**

- [ ] Passer à PostgreSQL
- [ ] Ajouter une 2e source météo
- [ ] Exposer une API REST ou export Power BI
- [ ] Introduire structures de données (queue, DAG, index temporel)

---

## Règle d’or
Toujours avancer dans cet ordre :

**Domain → Use case → Test → Adapter → CLI**

Ne jamais sauter une étape.
