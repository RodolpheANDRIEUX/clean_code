# Weather ETL – V1

Petit projet pour apprendre l’architecture hexagonale en Python.

L’application permet de :
- sélectionner des stations météo
- récupérer leurs données via l’API Toulouse Métropole
- stocker les données brutes dans SQLite (ODS)
- tracer chaque ingestion par batch

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

## 3) Inspecter l’ODS

Statistiques :

```bash
python -m src.adapters.cli.main ods stats
```

Voir un échantillon :

```bash
python -m src.adapters.cli.main ods sample --n 10
```

---

# Ce que fait l’application

- Elle appelle l’API météo.
- Elle filtre les données selon la fenêtre temporelle.
- Elle stocke le JSON brut sans transformation.
- Elle évite les doublons.
- Elle enregistre chaque ingestion comme un batch traçable.

---

# Ce que l’application ne fait pas encore

- Pas de données nettoyées (DWH)
- Pas de visualisation
- Pas de prédiction
- Pas d’API REST
