# 🧭 Conventions de dev
*(Parce que sans règles, même la météo devient imprévisible.)*

## 🧱 Structure
- Archi **hexagonale** : domaine pur, adapters coupables.
- `domain/` = logique métier, pas de pandas/SQL/HTTP.
- Pas de dossier “misc”.
- Des .md partout pour la doc.
- Des emojis partout parceque de toute facon c'est ChatGPT qui code.

## 💻 Code style
- **PEP8 + Typage**.
- Nommage :

  | Élément        | Convention / Exemple                | À éviter / Pourquoi |
  |----------------|-------------------------------------|---------------------|
  | **Classe**     | `StationRepository`, `Prevision`    | `DataManager`, `Helper` — trop vague |
  | **Variable**   | `temperature_actuelle`              | `tmp`, `x`, `data2` — pas de sens |
  | **Constante**  | `MAX_HUMIDITE = 100`                | `maxHumi` — pas lisible ni standard |
  | **Fonction**   | `calculer_prevision()`, `charger_donnees()` | `doStuff()`, `runAll()` — trop flou |
  | **Booléen**    | `is_active`, `has_error`            | `flag`, `ok`, `test` — ambigu |
  | **Module/Fichier** | `station_repository.py`, `prevision_service.py` | `utils.py`, `misc.py` — poubelle à tout faire |
  | **Variable globale** | constantes (`APP_MODE = "DEV"`) | `global_data` — couplage et chaos |


## 🪶 Git
Branches :  
`main` (stable) · `dev` · `feature/*` · `fix/*`

Commits :

```
<type>(<scope>?): <title>

<body> 
``` 

Types : feat | fix | docs | refactor | test

Ex : `feat(#12): add station fetcher`

>  Scope (optional) refers to my private todo list item number

## 🧪 Tests

- MVP : data tests only (schémas, bornes, nulls).

- Pas de tests unitaires, mais zéro donnée sale.

## 🪵 Logs (wood log hehe do you get it)

- 2 modes : DEV verbeux / PROD propre.

- JSON structuré, jamais de secrets.

## 🧹 Clean code

- SOLID, KISS, DRY, YAGNI.