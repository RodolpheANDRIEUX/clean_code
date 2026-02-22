# Weather ETL – V1

Petit projet pour apprendre l'architecture hexagonale en Python.

L'application permet de :
- sélectionner des stations météo
- récupérer leurs données via l'API Toulouse Métropole
- stocker les données brutes dans SQLite (ODS)
- tracer chaque ingestion par batch

> 📐 [Design Patterns utilisés dans ce projet](design_patterns.md)

---


# Commandes disponibles

## 1) Lister les stations sélectionnées

```bash
python -m src.adapters.cli.main stations list-selected
```

Options utiles :
- `--max-datasets 50`
- `--whitelist 1,3,5`
- `--allow-other-types`

---

## 2) Ingestion des données

Récupère les observations sur une fenêtre de temps et les stocke en base.

```bash
python -m src.adapters.cli.main ingest latest \
  --since "2025-12-01T07:00:00+00:00" \
  --until "2025-12-01T10:00:00+00:00"
```

Options utiles :
- `--whitelist 1,3`
- `--sqlite-path data/app.sqlite`

Sortie typique :

```
batch_id=...
stations=12
inserted=55000 rejected=12
window=[2025-12-01T07:00:00+00:00 → 2025-12-01T10:00:00+00:00)
```

---

## 3) Inspecter l'ODS

Statistiques :

```bash
python -m src.adapters.cli.main ods stats
```

Voir un échantillon :

```bash
python -m src.adapters.cli.main ods sample --n 10
```

---

## 4) Consulter les données

Stations en base :

```bash
python -m src.adapters.cli.main data stations
```

Dernière mesure de chaque station :

```bash
python -m src.adapters.cli.main data latest
```

Mesures d'une station (les 20 dernières par défaut) :

```bash
python -m src.adapters.cli.main data show 3
python -m src.adapters.cli.main data show 3 --n 50
```

---

## 5) Data Profiling

Analyse le contenu de l'ODS et génère un rapport (console + HTML).

```bash
python scripts/run_data_profile.py
```

Options :
- `--text-only` → terminal uniquement, pas de HTML
- `--output path/to/report.html` → chemin du rapport (défaut : `scripts/data_profile.html`)
- `--sample 5000` → sous-ensemble de lignes pour aller plus vite

Le rapport couvre : nulls, bornes métier, min/max/moyenne/médiane/std, gaps temporels par station, doublons.

---

# Ce que fait l'application

- Elle appelle l'API météo.
- Elle filtre les données selon la fenêtre temporelle.
- Elle stocke le JSON brut sans transformation.
- Elle évite les doublons.
- Elle enregistre chaque ingestion comme un batch traçable.

---

# Ce que l'application ne fait pas encore

- Pas de données nettoyées (DWH)
- Pas de visualisation
- Pas de prédiction
- Pas d'API REST
