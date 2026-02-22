from __future__ import annotations

import typer

from src.adapters.cli.stations import app as stations_app
from src.adapters.cli.ingest import app as ingest_app
from src.adapters.cli.ods import app as ods_app
from src.adapters.cli.data import app as data_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(stations_app, name="stations")
app.add_typer(ingest_app, name="ingest")
app.add_typer(ods_app, name="ods")
app.add_typer(data_app, name="data")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
