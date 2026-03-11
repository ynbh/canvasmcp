from __future__ import annotations

import json
import os
from typing import Annotated, Any

import typer
from rich.console import Console

from canvas_api import ensure_canvas_auth_configured
from canvas_tools import TOOL_SPECS, dispatch_tool_call

app = typer.Typer(
    help="Canvas CLI for local Canvas LMS workflows.",
    no_args_is_help=True,
    rich_markup_mode="markdown",
)
course_app = typer.Typer(help="Course-level commands.")
assignments_app = typer.Typer(help="Assignment commands.")
discussion_app = typer.Typer(help="Discussion commands.")
files_app = typer.Typer(help="File and folder commands.")
cli_tool_app = typer.Typer(help="Low-level tool access.")

app.add_typer(course_app, name="course")
app.add_typer(assignments_app, name="assignments")
app.add_typer(discussion_app, name="discussion")
app.add_typer(files_app, name="files")
app.add_typer(cli_tool_app, name="tool")

console = Console()
TOOL_NAMES = sorted(spec.name for spec in TOOL_SPECS)


def _ensure_auth() -> None:
    ensure_canvas_auth_configured()


def _print_result(result: dict[str, Any]) -> None:
    if "error" in result:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")
        raise typer.Exit(1)
    console.print_json(json.dumps(result, default=str))


def _invoke(tool_name: str, args: dict[str, Any] | None = None) -> None:
    if tool_name != "get_today":
        _ensure_auth()
    _print_result(dispatch_tool_call(tool_name, args or {}))


def _parse_json(value: str | None, *, flag_name: str) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        console.print(f"[bold red]Invalid JSON for {flag_name}:[/bold red] {exc}")
        raise typer.Exit(2) from exc


@app.command()
def today() -> None:
    """Show today's date."""
    _invoke("get_today")


@app.command("courses")
def list_courses(
    all_courses: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Include active enrollments instead of favorites only.",
        ),
    ] = False,
    search: Annotated[str | None, typer.Option(help="Filter by course name/code.")] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of courses to return.")] = 50,
) -> None:
    """List your courses."""
    _invoke(
        "list_courses",
        {
            "favorites_only": not all_courses,
            "search": search,
            "limit": limit,
        },
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
    """Resolve a fuzzy course query."""
    _invoke(
        "resolve_course",
        {
            "query": query,
            "favorites_only": not all_courses,
            "limit": limit,
        },
    )


@course_app.command("overview")
def course_overview(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")]
) -> None:
    """Show course metadata and teachers."""
    _invoke("get_course_overview", {"course_id": course_id})


@course_app.command("syllabus")
def course_syllabus(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    with_body: Annotated[
        bool,
        typer.Option("--body/--no-body", help="Include syllabus HTML body."),
    ] = True,
    body_char_limit: Annotated[
        int,
        typer.Option(help="Maximum syllabus body characters."),
    ] = 12000,
) -> None:
    """Show course syllabus."""
    _invoke(
        "get_course_syllabus",
        {
            "course_id": course_id,
            "include_body": with_body,
            "body_char_limit": body_char_limit,
        },
    )


@course_app.command("context")
def course_context(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    include_syllabus_body: Annotated[
        bool,
        typer.Option("--body/--no-body", help="Include syllabus body in snapshot."),
    ] = False,
    upcoming_limit: Annotated[int, typer.Option(help="Upcoming assignments limit.")] = 20,
    announcements_limit: Annotated[
        int, typer.Option(help="Announcements limit.")
    ] = 10,
    modules_limit: Annotated[int, typer.Option(help="Modules limit.")] = 20,
    module_items_limit: Annotated[
        int, typer.Option(help="Module items limit.")
    ] = 50,
) -> None:
    """Show an aggregated course snapshot."""
    _invoke(
        "get_course_context_snapshot",
        {
            "course_id": course_id,
            "include_syllabus_body": include_syllabus_body,
            "upcoming_limit": upcoming_limit,
            "announcements_limit": announcements_limit,
            "modules_limit": modules_limit,
            "module_items_limit": module_items_limit,
        },
    )


@course_app.command("pages")
def course_pages(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    search: Annotated[str | None, typer.Option(help="Filter by page title/url.")] = None,
    published_only: Annotated[
        bool | None,
        typer.Option(
            "--published",
            help="Only published pages. Omit to include both published and unpublished.",
        ),
    ] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of pages.")] = 100,
) -> None:
    """List course pages."""
    _invoke(
        "list_course_pages",
        {
            "course_id": course_id,
            "search": search,
            "published_only": published_only,
            "limit": limit,
        },
    )


@course_app.command("page")
def course_page(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    url_or_id: Annotated[str, typer.Argument(help="Page URL slug or page ID.")],
    force_as_id: Annotated[
        bool, typer.Option(help="Treat the second argument strictly as a page ID.")
    ] = False,
) -> None:
    """Fetch one course page."""
    _invoke(
        "canvas_get_page",
        {
            "course_id": course_id,
            "url_or_id": url_or_id,
            "force_as_id": force_as_id,
        },
    )


@course_app.command("tabs")
def course_tabs(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    limit: Annotated[int, typer.Option(help="Maximum number of tabs.")] = 100,
) -> None:
    """List course navigation tabs."""
    _invoke("list_course_tabs", {"course_id": course_id, "limit": limit})


@course_app.command("tab")
def course_tab(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    tab_id: Annotated[str, typer.Argument(help="Tab ID, such as home or modules.")],
    include_target: Annotated[
        bool, typer.Option("--target/--no-target", help="Resolve the tab destination.")
    ] = True,
) -> None:
    """Fetch one course tab."""
    _invoke(
        "get_course_tab",
        {
            "course_id": course_id,
            "tab_id": tab_id,
            "include_target": include_target,
        },
    )


@course_app.command("people")
def course_people(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    search: Annotated[str | None, typer.Option(help="Filter by person name/email.")] = None,
    enrollment_type: Annotated[
        list[str] | None,
        typer.Option(
            "--role",
            help="Enrollment type filter. Repeat for multiple roles.",
        ),
    ] = None,
    include_email: Annotated[
        bool, typer.Option("--email/--no-email", help="Include email addresses.")
    ] = True,
    limit: Annotated[int, typer.Option(help="Maximum number of people.")] = 100,
) -> None:
    """List people in a course."""
    _invoke(
        "list_course_people",
        {
            "course_id": course_id,
            "search": search,
            "enrollment_types": enrollment_type or [],
            "include_email": include_email,
            "limit": limit,
        },
    )


@course_app.command("modules")
def course_modules(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    search: Annotated[str | None, typer.Option(help="Filter by module name.")] = None,
    include_items: Annotated[
        bool, typer.Option("--items/--no-items", help="Include module items.")
    ] = False,
    include_content_details: Annotated[
        bool,
        typer.Option(
            "--details/--no-details",
            help="Include Canvas content details for module items.",
        ),
    ] = False,
    limit: Annotated[int, typer.Option(help="Maximum number of modules.")] = 100,
    items_limit: Annotated[
        int, typer.Option(help="Maximum number of items per module.")
    ] = 100,
) -> None:
    """List course modules."""
    _invoke(
        "list_modules",
        {
            "course_id": course_id,
            "search": search,
            "include_items": include_items,
            "include_content_details": include_content_details,
            "limit": limit,
            "items_limit": items_limit,
        },
    )


@course_app.command("grades")
def course_grades(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    student_id: Annotated[str, typer.Option(help="Canvas student ID.")] = "self",
) -> None:
    """Show grade summary for a course."""
    _invoke(
        "get_course_grade_summary",
        {"course_id": course_id, "student_id": student_id},
    )


@course_app.command("submissions")
def course_submissions(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    student_id: Annotated[str, typer.Option(help="Canvas student ID.")] = "self",
    assignment_id: Annotated[
        list[str] | None,
        typer.Option("--assignment", help="Assignment ID filter. Repeat as needed."),
    ] = None,
    include: Annotated[
        list[str] | None,
        typer.Option("--include", help="Submission include values. Repeat as needed."),
    ] = None,
    grouped: Annotated[
        bool, typer.Option(help="Keep Canvas grouped submission shells.")
    ] = False,
    workflow_state: Annotated[
        str | None, typer.Option(help="Submission workflow state filter.")
    ] = None,
    submitted_since: Annotated[
        str | None, typer.Option(help="ISO datetime lower bound.")
    ] = None,
    graded_since: Annotated[
        str | None, typer.Option(help="ISO datetime lower bound.")
    ] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of submissions.")] = 200,
) -> None:
    """List submissions for a course."""
    _invoke(
        "list_course_submissions",
        {
            "course_id": course_id,
            "student_id": student_id,
            "assignment_ids": assignment_id or [],
            "include": include or [],
            "grouped": grouped,
            "workflow_state": workflow_state,
            "submitted_since": submitted_since,
            "graded_since": graded_since,
            "limit": limit,
        },
    )


@assignments_app.command("list")
def assignments_list(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    search: Annotated[str | None, typer.Option(help="Filter by assignment name.")] = None,
    bucket: Annotated[
        str | None, typer.Option(help="Bucket: upcoming, overdue, past, etc.")
    ] = None,
    include_submission: Annotated[
        bool, typer.Option(help="Include current user's submission where available.")
    ] = False,
    limit: Annotated[int, typer.Option(help="Maximum number of assignments.")] = 100,
) -> None:
    """List assignments in a course."""
    _invoke(
        "list_course_assignments",
        {
            "course_id": course_id,
            "search": search,
            "bucket": bucket,
            "include_submission": include_submission,
            "limit": limit,
        },
    )


@assignments_app.command("show")
def assignments_show(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    assignment_id: Annotated[str, typer.Argument(help="Assignment ID.")],
    include_submission: Annotated[
        bool, typer.Option(help="Include current user's submission where available.")
    ] = False,
) -> None:
    """Show one assignment."""
    _invoke(
        "get_assignment_details",
        {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "include_submission": include_submission,
        },
    )


@assignments_app.command("groups")
def assignments_groups(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    include_assignments: Annotated[
        bool, typer.Option("--assignments/--no-assignments", help="Include assignments.")
    ] = False,
    include_submission: Annotated[
        bool, typer.Option(help="Include submission data when available.")
    ] = False,
    limit: Annotated[int, typer.Option(help="Maximum number of groups.")] = 100,
) -> None:
    """List assignment groups."""
    _invoke(
        "list_assignment_groups",
        {
            "course_id": course_id,
            "include_assignments": include_assignments,
            "include_submission": include_submission,
            "limit": limit,
        },
    )


@discussion_app.command("list")
def discussion_list(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    search: Annotated[str | None, typer.Option(help="Search title or title/message.")] = None,
    graded_only: Annotated[
        bool, typer.Option("--graded", help="Only include graded discussions.")
    ] = False,
    exact_title: Annotated[
        bool, typer.Option(help="Require exact title match when searching.")
    ] = False,
    include_announcements: Annotated[
        bool, typer.Option(help="Include announcement topics.")
    ] = False,
    search_in: Annotated[
        str,
        typer.Option(help="Search mode: title or title_or_message."),
    ] = "title",
    limit: Annotated[int, typer.Option(help="Maximum number of topics.")] = 100,
) -> None:
    """List discussion topics."""
    _invoke(
        "list_discussion_topics",
        {
            "course_id": course_id,
            "search": search,
            "only_graded": graded_only,
            "exact_title": exact_title,
            "include_announcements": include_announcements,
            "search_in": search_in,
            "limit": limit,
        },
    )


@discussion_app.command("show")
def discussion_show(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    topic_id: Annotated[str, typer.Argument(help="Discussion topic ID.")],
    include_replies: Annotated[
        bool, typer.Option("--replies/--no-replies", help="Include nested replies.")
    ] = True,
    include_participants: Annotated[
        bool,
        typer.Option(
            "--participants/--no-participants",
            help="Include discussion participant metadata.",
        ),
    ] = True,
    limit: Annotated[int, typer.Option(help="Maximum entries to return.")] = 200,
) -> None:
    """Show discussion entries."""
    _invoke(
        "get_discussion_entries",
        {
            "course_id": course_id,
            "topic_id": topic_id,
            "include_replies": include_replies,
            "include_participants": include_participants,
            "limit": limit,
        },
    )


@files_app.command("list")
def files_list(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    search: Annotated[str | None, typer.Option(help="Filter by file name.")] = None,
    sort: Annotated[str | None, typer.Option(help="Sort key.")] = None,
    order: Annotated[str | None, typer.Option(help="Sort order: asc or desc.")] = None,
    limit: Annotated[int, typer.Option(help="Maximum number of files.")] = 100,
) -> None:
    """List course files."""
    _invoke(
        "list_course_files",
        {
            "course_id": course_id,
            "search": search,
            "sort": sort,
            "order": order,
            "limit": limit,
        },
    )


@files_app.command("download")
def files_download(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    file_id: Annotated[str, typer.Argument(help="Canvas file ID.")],
    force_refresh: Annotated[
        bool, typer.Option(help="Redownload even if a cached local copy exists.")
    ] = False,
) -> None:
    """Download one file into local temp storage."""
    _invoke(
        "download_course_file",
        {
            "course_id": course_id,
            "file_id": file_id,
            "force_refresh": force_refresh,
        },
    )


@files_app.command("folders")
def files_folders(
    course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
    limit: Annotated[int, typer.Option(help="Maximum number of folders.")] = 150,
) -> None:
    """List course folders."""
    _invoke("list_course_folders", {"course_id": course_id, "limit": limit})


@app.command()
def announcements(
    course_id: Annotated[
        list[str],
        typer.Option("--course", help="Course ID. Repeat for multiple courses."),
    ],
    start_date: Annotated[str | None, typer.Option(help="ISO datetime lower bound.")] = None,
    end_date: Annotated[str | None, typer.Option(help="ISO datetime upper bound.")] = None,
    active_only: Annotated[
        bool, typer.Option("--active/--all", help="Only active announcements.")
    ] = True,
    limit: Annotated[int, typer.Option(help="Maximum announcements.")] = 100,
) -> None:
    """List announcements across courses."""
    _invoke(
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
def calendar(
    course_id: Annotated[
        list[str] | None,
        typer.Option("--course", help="Course ID. Repeat for multiple courses."),
    ] = None,
    type: Annotated[
        str | None, typer.Option(help="event, assignment, or both.")
    ] = None,
    start_date: Annotated[str | None, typer.Option(help="ISO datetime lower bound.")] = None,
    end_date: Annotated[str | None, typer.Option(help="ISO datetime upper bound.")] = None,
    all_events: Annotated[
        bool | None,
        typer.Option(help="Request all matching events instead of the default filtered view."),
    ] = None,
    limit: Annotated[int, typer.Option(help="Maximum events.")] = 100,
) -> None:
    """List calendar events."""
    _invoke(
        "list_calendar_events",
        {
            "course_ids": course_id or [],
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
            "all_events": all_events,
            "limit": limit,
        },
    )


@app.command("url")
def resolve_url(
    url: Annotated[str, typer.Argument(help="Canvas URL to resolve.")],
    fetch_details: Annotated[
        bool, typer.Option("--details/--no-details", help="Fetch linked object details.")
    ] = True,
) -> None:
    """Resolve a Canvas URL into structured metadata."""
    _invoke("resolve_canvas_url", {"url": url, "fetch_details": fetch_details})


@cli_tool_app.command("list")
def tool_list() -> None:
    """List raw tool names exposed by the underlying handlers."""
    console.print_json(json.dumps({"tools": TOOL_NAMES}))


@cli_tool_app.command("run")
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
    """Run any underlying tool by name with raw JSON arguments."""
    if name not in TOOL_NAMES:
        console.print(f"[bold red]Unknown tool:[/bold red] {name}")
        console.print(f"Available tools: {', '.join(TOOL_NAMES)}")
        raise typer.Exit(2)
    parsed_args = _parse_json(args, flag_name="--args")
    if not isinstance(parsed_args, dict):
        console.print("[bold red]Invalid JSON for --args:[/bold red] expected an object")
        raise typer.Exit(2)
    _invoke(name, parsed_args)


def main() -> None:
    app()


@app.command("auth-status")
def auth_status() -> None:
    """Show the current auth mode and Canvas base URL override."""
    base_url = os.getenv("CANVAS_BASE_URL", "").strip() or None
    mode = ensure_canvas_auth_configured()
    console.print_json(json.dumps({"auth_mode": mode, "canvas_base_url": base_url}))


if __name__ == "__main__":
    main()
