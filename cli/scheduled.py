from __future__ import annotations

import json

import typer
from rich.console import Console

console = Console()

scheduled_app = typer.Typer(
    name="scheduled",
    help="Internal launchd entrypoints for scheduled submits.",
    hidden=True,
    no_args_is_help=True,
)


@scheduled_app.command("fire", hidden=True)
def scheduled_fire(
    job_id: str = typer.Argument(..., help="Scheduled job id."),
) -> None:
    from schedule.fire import fire_job

    result = fire_job(job_id)
    console.print_json(json.dumps(result, default=str))
    if isinstance(result, dict) and result.get("error"):
        raise typer.Exit(1)
