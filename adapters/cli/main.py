from __future__ import annotations

import typer

from adapters.cli.stations import app as stations_app
from adapters.cli.ingest import app as ingest_app
from adapters.cli.ods import app as ods_app

app = typer.Typer(no_args_is_help=True)
app.add_typer(stations_app, name="stations")
app.add_typer(ingest_app, name="ingest")
app.add_typer(ods_app, name="ods")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
