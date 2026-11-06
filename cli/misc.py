from __future__ import annotations

import json
from typing import Annotated

import typer

from auth import CanvasAPIError, get_auth_status
from cli.output import emit, fail, invoke
from specs.registry import TOOL_SPECS

misc_app = typer.Typer()
tool_app = typer.Typer(help="Low-level tool access.")
TOOL_NAMES = sorted(spec.name for spec in TOOL_SPECS)


def safe_auth_status() -> dict[str, object]:
    try:
        return get_auth_status()
    except CanvasAPIError as exc:
        return {
            "auth_mode": None,
            "auth_verified": False,
            "auth_status": "error",
            "error": str(exc),
        }


@misc_app.command()
def today() -> None:
    invoke("get_today")


@misc_app.command("courses")
def list_courses(
    all_courses: Annotated[
        bool,
        typer.Option(
            "--all", help="Include active enrollments instead of favorites only."
        ),
    ] = False,
    search: Annotated[
        str | None, typer.Option(help="Filter by course name/code.")
    ] = None,
    limit: Annotated[
        int, typer.Option(help="Maximum number of courses to return.")
    ] = 50,
) -> None:
    invoke(
        "list_courses",
        {"favorites_only": not all_courses, "search": search, "limit": limit},
    )


@misc_app.command()
def resolve(
    query: Annotated[str, typer.Argument(help="Course name/code query.")],
    all_courses: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Search active enrollments instead of favorites only.",
        ),
    ] = False,
    limit: Annotated[int, typer.Option(help="Maximum matches to return.")] = 5,
) -> None:
    invoke(
        "resolve_course",
        {"query": query, "favorites_only": not all_courses, "limit": limit},
    )


@misc_app.command()
def announcements(
    course_id: Annotated[
        list[str],
        typer.Option("--course", help="Course ID. Repeat for multiple courses."),
    ],
    start_date: Annotated[
        str | None, typer.Option(help="ISO datetime lower bound.")
    ] = None,
    end_date: Annotated[
        str | None, typer.Option(help="ISO datetime upper bound.")
    ] = None,
    active_only: Annotated[
        bool, typer.Option("--active/--all", help="Only active announcements.")
    ] = True,
    limit: Annotated[int, typer.Option(help="Maximum announcements.")] = 100,
) -> None:
    invoke(
        "list_announcements",
        {
            "course_ids": course_id,
            "start_date": start_date,
            "end_date": end_date,
            "active_only": active_only,
            "limit": limit,
        },
    )


@misc_app.command()
def todo(
    course_id: Annotated[
        list[str] | None,
        typer.Option("--course", help="Course ID. Repeat for multiple courses."),
    ] = None,
    limit: Annotated[int, typer.Option(help="Maximum To Do items.")] = 100,
) -> None:
    invoke(
        "list_todo_items",
        {
            "course_ids": course_id or [],
            "limit": limit,
        },
    )


@misc_app.command("url")
def resolve_url(
    url: Annotated[str, typer.Argument(help="Canvas URL to resolve.")],
    fetch_details: Annotated[
        bool,
        typer.Option("--details/--no-details", help="Fetch linked object details."),
    ] = True,
) -> None:
    invoke("resolve_canvas_url", {"url": url, "fetch_details": fetch_details})


@misc_app.command("auth-status")
def auth_status() -> None:
    emit(safe_auth_status(), tool_name="auth_status", failures=False)


@tool_app.command("list")
def tool_list() -> None:
    emit({"tools": TOOL_NAMES}, tool_name="tool_list")


@tool_app.command("run")
def tool_run(
    name: Annotated[str, typer.Argument(help="Underlying tool name.")],
    args: Annotated[
        str,
        typer.Option(
            "--args",
            help='JSON object of tool arguments, for example \'{"course_id":"123"}\'.',
        ),
    ] = "{}",
) -> None:
    if name not in TOOL_NAMES:
        fail("unknown_tool", f"Unknown tool: {name}", exit_code=2, tools=TOOL_NAMES)
    try:
        parsed_args = json.loads(args)
    except json.JSONDecodeError as exc:
        fail("invalid_json", f"Invalid JSON for --args: {exc}", exit_code=2)
    if not isinstance(parsed_args, dict):
        fail(
            "invalid_json",
            "Invalid JSON for --args: expected an object",
            exit_code=2,
        )
    invoke(name, parsed_args)
