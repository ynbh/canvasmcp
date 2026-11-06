from __future__ import annotations

from typing import Annotated

import typer

from cli.assignments import assignments_app
from cli.courses import course_app
from cli.discussions import discussion_app
from cli.files import files_app
from cli.inbox import inbox_app
from cli.misc import misc_app, tool_app
from cli.output import OutputMode
from cli.scheduled import scheduled_app
from cli.settings import settings_app

app = typer.Typer(
    help="Canvas CLI for local Canvas LMS workflows.",
    no_args_is_help=True,
    rich_markup_mode="markdown",
)
app.add_typer(misc_app)
app.add_typer(course_app, name="course")
app.add_typer(assignments_app, name="assignments")
app.add_typer(discussion_app, name="discussion")
app.add_typer(files_app, name="files")
app.add_typer(inbox_app, name="inbox")
app.add_typer(tool_app, name="tool")
app.add_typer(settings_app, name="settings")
app.add_typer(scheduled_app, name="scheduled")


@app.callback()
def configure_output(
    ctx: typer.Context,
    output: Annotated[
        OutputMode,
        typer.Option(
            "--output",
            envvar="CANVAS_OUTPUT",
            help="Result format. Auto uses pretty for terminal stdout and JSON otherwise.",
        ),
    ] = OutputMode.auto,
) -> None:
    ctx.meta["output"] = output
    ctx.meta["machine_output"] = ctx.invoked_subcommand in {"tool", "scheduled"}


def main() -> None:
    app()


if __name__ == "__main__":
    main()
