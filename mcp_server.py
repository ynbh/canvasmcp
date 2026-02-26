from __future__ import annotations

from fastmcp import FastMCP
import os
from typing import Literal

from canvas_api import ensure_canvas_auth_configured
from canvas_tools import dispatch_tool_call

mcp = FastMCP("canvas-mcp")

Transport = Literal["stdio", "http", "sse", "streamable-http"]

ENV_MCP_TRANSPORT = "MCP_TRANSPORT"
ENV_MCP_HOST = "MCP_HOST"
ENV_MCP_PORT = "MCP_PORT"

DEFAULT_TRANSPORT: Transport = "stdio"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

HTTP_STYLE_TRANSPORTS: set[Transport] = {"http", "sse", "streamable-http"}
SUPPORTED_TRANSPORTS: set[Transport] = {DEFAULT_TRANSPORT, *HTTP_STYLE_TRANSPORTS}


# tool: return today's date in iso format.
@mcp.tool()
def get_today() -> dict:
    return dispatch_tool_call("get_today")


# tool: list favorite or active courses for the current user.
@mcp.tool()
def list_courses(
    favorites_only: bool = True,
    search: str | None = None,
    limit: int = 50,
) -> dict:
    return dispatch_tool_call(
        "list_courses",
        {"favorites_only": favorites_only, "search": search, "limit": limit},
    )


# tool: resolve a natural-language query to one or more course matches.
@mcp.tool()
def resolve_course(
    query: str,
    favorites_only: bool = True,
    limit: int = 5,
) -> dict:
    return dispatch_tool_call(
        "resolve_course",
        {"query": query, "favorites_only": favorites_only, "limit": limit},
    )


# tool: return course metadata and teacher info for quick context.
@mcp.tool()
def get_course_overview(course_id: str) -> dict:
    return dispatch_tool_call("get_course_overview", {"course_id": course_id})


# tool: return course syllabus metadata and optional syllabus body html.
@mcp.tool()
def get_course_syllabus(
    course_id: str,
    include_body: bool = True,
    body_char_limit: int = 12000,
) -> dict:
    return dispatch_tool_call(
        "get_course_syllabus",
        {
            "course_id": course_id,
            "include_body": include_body,
            "body_char_limit": body_char_limit,
        },
    )


# tool: list assignments in a course with optional filtering.
@mcp.tool()
def list_course_assignments(
    course_id: str,
    search: str | None = None,
    bucket: str | None = None,
    include_submission: bool = False,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_course_assignments",
        {
            "course_id": course_id,
            "search": search,
            "bucket": bucket,
            "include_submission": include_submission,
            "limit": limit,
        },
    )


# tool: return complete details for one assignment.
@mcp.tool()
def get_assignment_details(
    course_id: str,
    assignment_id: str,
    include_submission: bool = False,
) -> dict:
    return dispatch_tool_call(
        "get_assignment_details",
        {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "include_submission": include_submission,
        },
    )


# tool: list course pages for discovery before fetching a specific page.
@mcp.tool()
def list_course_pages(
    course_id: str,
    search: str | None = None,
    published_only: bool | None = None,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_course_pages",
        {
            "course_id": course_id,
            "search": search,
            "published_only": published_only,
            "limit": limit,
        },
    )


# tool: fetch a single course wiki page by slug or page id.
@mcp.tool()
def canvas_get_page(
    course_id: str,
    url_or_id: str,
    force_as_id: bool = False,
) -> dict:
    return dispatch_tool_call(
        "canvas_get_page",
        {
            "course_id": course_id,
            "url_or_id": url_or_id,
            "force_as_id": force_as_id,
        },
    )


# tool: list discussion topics for a course.
@mcp.tool()
def list_discussion_topics(
    course_id: str,
    search: str | None = None,
    only_graded: bool = False,
    exact_title: bool = False,
    include_announcements: bool = False,
    search_in: str = "title",
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_discussion_topics",
        {
            "course_id": course_id,
            "search": search,
            "only_graded": only_graded,
            "exact_title": exact_title,
            "include_announcements": include_announcements,
            "search_in": search_in,
            "limit": limit,
        },
    )


# tool: return discussion entries with optional replies and participants.
@mcp.tool()
def get_discussion_entries(
    course_id: str,
    topic_id: str,
    include_replies: bool = True,
    include_participants: bool = True,
    limit: int = 200,
) -> dict:
    return dispatch_tool_call(
        "get_discussion_entries",
        {
            "course_id": course_id,
            "topic_id": topic_id,
            "include_replies": include_replies,
            "include_participants": include_participants,
            "limit": limit,
        },
    )


# tool: list course files with optional search and sort.
@mcp.tool()
def list_course_files(
    course_id: str,
    search: str | None = None,
    sort: str | None = None,
    order: str | None = None,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_course_files",
        {
            "course_id": course_id,
            "search": search,
            "sort": sort,
            "order": order,
            "limit": limit,
        },
    )


# tool: download a file from a course into local temp storage.
@mcp.tool()
def download_course_file(
    course_id: str,
    file_id: str,
    force_refresh: bool = False,
) -> dict:
    return dispatch_tool_call(
        "download_course_file",
        {
            "course_id": course_id,
            "file_id": file_id,
            "force_refresh": force_refresh,
        },
    )


# tool: list folders in a course.
@mcp.tool()
def list_course_folders(course_id: str, limit: int = 150) -> dict:
    return dispatch_tool_call(
        "list_course_folders",
        {"course_id": course_id, "limit": limit},
    )


# tool: list assignment groups and optionally include assignments/submissions.
@mcp.tool()
def list_assignment_groups(
    course_id: str,
    include_assignments: bool = False,
    include_submission: bool = False,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_assignment_groups",
        {
            "course_id": course_id,
            "include_assignments": include_assignments,
            "include_submission": include_submission,
            "limit": limit,
        },
    )


# tool: list submissions for a student in a course.
@mcp.tool()
def list_course_submissions(
    course_id: str,
    student_id: str = "self",
    assignment_ids: list[str] | None = None,
    include: list[str] | None = None,
    grouped: bool = False,
    workflow_state: str | None = None,
    submitted_since: str | None = None,
    graded_since: str | None = None,
    limit: int = 200,
) -> dict:
    return dispatch_tool_call(
        "list_course_submissions",
        {
            "course_id": course_id,
            "student_id": student_id,
            "assignment_ids": assignment_ids or [],
            "include": include or [],
            "grouped": grouped,
            "workflow_state": workflow_state,
            "submitted_since": submitted_since,
            "graded_since": graded_since,
            "limit": limit,
        },
    )


# tool: summarize course grade data and assignment-group performance.
@mcp.tool()
def get_course_grade_summary(course_id: str, student_id: str = "self") -> dict:
    return dispatch_tool_call(
        "get_course_grade_summary",
        {"course_id": course_id, "student_id": student_id},
    )


# tool: list modules with optional module items and content details.
@mcp.tool()
def list_modules(
    course_id: str,
    search: str | None = None,
    include_items: bool = False,
    include_content_details: bool = False,
    limit: int = 100,
    items_limit: int = 100,
) -> dict:
    return dispatch_tool_call(
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


# tool: list announcements for one or more courses.
@mcp.tool()
def list_announcements(
    course_ids: list[str],
    start_date: str | None = None,
    end_date: str | None = None,
    active_only: bool = True,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_announcements",
        {
            "course_ids": course_ids,
            "start_date": start_date,
            "end_date": end_date,
            "active_only": active_only,
            "limit": limit,
        },
    )


# tool: list calendar events and assignment events across courses.
@mcp.tool()
def list_calendar_events(
    course_ids: list[str] | None = None,
    type: str | None = None,  # noqa: A002
    start_date: str | None = None,
    end_date: str | None = None,
    all_events: bool | None = None,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_calendar_events",
        {
            "course_ids": course_ids or [],
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
            "all_events": all_events,
            "limit": limit,
        },
    )


# tool: list users in a course with enrollment metadata.
@mcp.tool()
def list_course_people(
    course_id: str,
    search: str | None = None,
    enrollment_types: list[str] | None = None,
    include_email: bool = True,
    limit: int = 100,
) -> dict:
    return dispatch_tool_call(
        "list_course_people",
        {
            "course_id": course_id,
            "search": search,
            "enrollment_types": enrollment_types or [],
            "include_email": include_email,
            "limit": limit,
        },
    )


# tool: parse a canvas url and optionally fetch linked object details.
@mcp.tool()
def resolve_canvas_url(url: str, fetch_details: bool = True) -> dict:
    return dispatch_tool_call(
        "resolve_canvas_url",
        {"url": url, "fetch_details": fetch_details},
    )


# tool: aggregate a compact course context snapshot for planning and review.
@mcp.tool()
def get_course_context_snapshot(
    course_id: str,
    include_syllabus_body: bool = False,
    upcoming_limit: int = 20,
    announcements_limit: int = 10,
    modules_limit: int = 20,
    module_items_limit: int = 50,
) -> dict:
    return dispatch_tool_call(
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


def _read_transport() -> Transport:
    raw = os.getenv(ENV_MCP_TRANSPORT, DEFAULT_TRANSPORT).strip().lower()
    transport = raw or DEFAULT_TRANSPORT
    if transport == "stdio":
        return "stdio"
    if transport == "http":
        return "http"
    if transport == "sse":
        return "sse"
    if transport == "streamable-http":
        return "streamable-http"
    raise RuntimeError(
        "Unsupported MCP_TRANSPORT. Use one of: stdio, http, sse, streamable-http."
    )


def _read_host_and_port() -> tuple[str, int]:
    host = os.getenv(ENV_MCP_HOST, DEFAULT_HOST).strip() or DEFAULT_HOST
    port_raw = os.getenv(ENV_MCP_PORT, str(DEFAULT_PORT)).strip() or str(DEFAULT_PORT)
    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid {ENV_MCP_PORT}: {port_raw}") from exc
    return host, port


def main() -> None:
    ensure_canvas_auth_configured()
    transport = _read_transport()

    if transport == "stdio":
        mcp.run()
        return

    if transport in HTTP_STYLE_TRANSPORTS:
        host, port = _read_host_and_port()
        mcp.run(transport=transport, host=host, port=port)
        return

    raise RuntimeError("Invalid transport state")


if __name__ == "__main__":
    main()
