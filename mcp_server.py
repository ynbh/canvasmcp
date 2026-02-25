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


@mcp.tool()
def get_today() -> dict:
    return dispatch_tool_call("get_today")


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


@mcp.tool()
def list_course_folders(course_id: str, limit: int = 150) -> dict:
    return dispatch_tool_call(
        "list_course_folders",
        {"course_id": course_id, "limit": limit},
    )


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
