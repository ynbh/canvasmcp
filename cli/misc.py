from __future__ import annotations

import json
from typing import Annotated, Callable

import typer
from rich.console import Console

from auth import CanvasAPIError

console = Console()
tool_app = typer.Typer(help="Low-level tool access.")


def register(
    app: typer.Typer,
    *,
    invoke: Callable[[str, dict | None], None],
    parse_json: Callable[[str | None], object],
    tool_names: list[str],
    auth_status_provider: Callable[[], dict[str, object]],
) -> typer.Typer:
    def _safe_auth_status() -> dict[str, object]:
        try:
            return auth_status_provider()
        except CanvasAPIError as exc:
            return {
                "auth_mode": None,
                "auth_verified": False,
                "auth_status": "error",
                "error": str(exc),
            }

    @app.command()
    def today() -> None:
        invoke("get_today")

    @app.command("courses")
    def list_courses(
        all_courses: Annotated[
            bool,
            typer.Option("--all", help="Include active enrollments instead of favorites only."),
        ] = False,
        search: Annotated[
            str | None, typer.Option(help="Filter by course name/code.")
        ] = None,
        limit: Annotated[int, typer.Option(help="Maximum number of courses to return.")] = 50,
    ) -> None:
        invoke(
            "list_courses",
            {"favorites_only": not all_courses, "search": search, "limit": limit},
        )

    @app.command()
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

    @app.command()
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

    @app.command()
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

    @app.command("url")
    def resolve_url(
        url: Annotated[str, typer.Argument(help="Canvas URL to resolve.")],
        fetch_details: Annotated[
            bool,
            typer.Option("--details/--no-details", help="Fetch linked object details."),
        ] = True,
    ) -> None:
        invoke("resolve_canvas_url", {"url": url, "fetch_details": fetch_details})

    @app.command("auth-status")
    def auth_status() -> None:
        console.print_json(json.dumps(_safe_auth_status(), default=str))

    @tool_app.command("list")
    def tool_list() -> None:
        console.print_json(json.dumps({"tools": tool_names}))

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
        if name not in tool_names:
            console.print(f"[bold red]Unknown tool:[/bold red] {name}")
            console.print(f"Available tools: {', '.join(tool_names)}")
            raise typer.Exit(2)
        parsed_args = parse_json(args)
        if not isinstance(parsed_args, dict):
            console.print("[bold red]Invalid JSON for --args:[/bold red] expected an object")
            raise typer.Exit(2)
        invoke(name, parsed_args)

    return tool_app
