"""Script de data profiling -- a lancer depuis la racine du projet.

    python scripts/run_data_profile.py
    python scripts/run_data_profile.py --output scripts/data_profile.html
    python scripts/run_data_profile.py --text-only

Genere un rapport HTML dans scripts/ (ou le chemin fourni).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# S'assure que la racine du projet est dans sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_tests.profiler import DataProfiler
from src.infrastructure.db import SqliteConfig, connect_sqlite


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Data Profiling -- ods_weather_raw")
    parser.add_argument(
        "--db",
        default="data/app.sqlite",
        help="Chemin vers le fichier SQLite (defaut: data/app.sqlite)",
    )
    parser.add_argument(
        "--output",
        default="scripts/data_profile.html",
        help="Chemin du rapport HTML genere (defaut: scripts/data_profile.html)",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Affiche uniquement le rapport texte dans le terminal, sans generer de HTML",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Limiter l'analyse a N lignes (utile pour tests rapides)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"[DB] Connexion a {args.db} ...")
    con = connect_sqlite(SqliteConfig(path=args.db))

    print("[PROFILER] Analyse en cours ...")
    profiler = DataProfiler(con, sample_size=args.sample)
    report = profiler.run()

    print(report.to_text())

    if not args.text_only:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report.to_html(), encoding="utf-8")
        print(f"\n[OK] Rapport HTML genere : {out_path.resolve()}")


if __name__ == "__main__":
    main()
