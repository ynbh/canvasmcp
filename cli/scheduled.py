from __future__ import annotations

import typer

from cli.output import emit

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
    emit(result, tool_name="scheduled_fire")
