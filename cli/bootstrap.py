from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console

from auth import CanvasAPIError, ensure_canvas_auth_configured, get_auth_status
from cli.assignments import assignments_app, register as register_assignments
from cli.courses import course_app, register as register_courses
from cli.discussions import discussion_app, register as register_discussions
from cli.files import files_app, register as register_files
from cli.misc import register as register_misc, tool_app as cli_tool_app
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

console = Console()
TOOL_NAMES = sorted(spec.name for spec in TOOL_SPECS)


def _ensure_auth() -> None:
    try:
        ensure_canvas_auth_configured()
    except CanvasAPIError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc


def _print_result(result: dict[str, Any]) -> None:
    if "error" in result:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")
        raise typer.Exit(1)
    console.print_json(json.dumps(result, default=str))


def _invoke(tool_name: str, args: dict[str, Any] | None = None) -> None:
    if tool_name != "get_today":
        _ensure_auth()
    try:
        _print_result(dispatch_tool_call(tool_name, args or {}))
    except CanvasAPIError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc


def _parse_json(value: str | None, *, flag_name: str) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        console.print(f"[bold red]Invalid JSON for {flag_name}:[/bold red] {exc}")
        raise typer.Exit(2) from exc


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
