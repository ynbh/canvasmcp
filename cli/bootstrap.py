from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from auth import CanvasAPIError, ensure_canvas_auth_configured, get_auth_status
from cli.assignments import assignments_app
from cli.assignments import register as register_assignments
from cli.courses import course_app
from cli.courses import register as register_courses
from cli.discussions import discussion_app
from cli.discussions import register as register_discussions
from cli.files import files_app
from cli.files import register as register_files
from cli.misc import register as register_misc
from cli.misc import tool_app as cli_tool_app
from cli.output import OutputMode, emit, fail
from cli.scheduled import scheduled_app
from cli.settings import settings_app
from specs.registry import TOOL_SPECS, dispatch_tool_call

app = typer.Typer(
    help="Canvas CLI for local Canvas LMS workflows.",
    no_args_is_help=True,
    rich_markup_mode="markdown",
)
app.add_typer(course_app, name="course")
app.add_typer(assignments_app, name="assignments")
app.add_typer(discussion_app, name="discussion")
app.add_typer(files_app, name="files")
app.add_typer(cli_tool_app, name="tool")
app.add_typer(settings_app, name="settings")
app.add_typer(scheduled_app, name="scheduled")

TOOL_NAMES = sorted(spec.name for spec in TOOL_SPECS)


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


def _ensure_auth() -> None:
    try:
        ensure_canvas_auth_configured()
    except CanvasAPIError as exc:
        fail("auth_error", str(exc))


def _invoke(tool_name: str, args: dict[str, Any] | None = None) -> None:
    if tool_name != "get_today":
        _ensure_auth()
    try:
        emit(dispatch_tool_call(tool_name, args or {}), tool_name=tool_name)
    except CanvasAPIError as exc:
        fail("canvas_api_error", str(exc))


def _parse_json(value: str | None, *, flag_name: str) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        fail("invalid_json", f"Invalid JSON for {flag_name}: {exc}", exit_code=2)


register_courses(_invoke)
register_assignments(_invoke)
register_discussions(_invoke)
register_files(_invoke)
register_misc(
    app,
    invoke=_invoke,
    parse_json=lambda value: _parse_json(value, flag_name="--args"),
    tool_names=TOOL_NAMES,
    auth_status_provider=lambda: get_auth_status(),
)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
