from __future__ import annotations

import typer

from src.application.ports.command import Command
from src.domain.model.station import Station
from src.infrastructure.wiring import build_get_selected_stations

app = typer.Typer(no_args_is_help=True)


@app.command("list-selected")
def list_selected(
        max_datasets: int = typer.Option(50, help="Limite le nombre de datasets catalog analyses."),
        allow_other_types: bool = typer.Option(False, help="Inclure StationType=OTHER."),
        whitelist: str = typer.Option("", help="IDs station separes par des virgules, ex: '1,3,5'."),
) -> None:
    wl_list: list[int] | None = None
    if whitelist.strip():
        wl_list = [int(x.strip()) for x in whitelist.split(",") if x.strip()]

    # GoF Command: le CLI (Invoker) manipule un Command[list[Station]]
    uc: Command[list[Station]] = build_get_selected_stations(
        max_datasets=max_datasets,
        allow_other_types=allow_other_types,
        whitelist=wl_list,
    )

    stations = uc.execute()
    for s in stations:
        print(f"{s.id.value}\t{s.station_type.value}\t{s.name}\t({s.dataset_id.value})")

