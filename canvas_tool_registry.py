from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from canvas_api import CanvasAPIError
from tools import (
    canvas_get_page,
    download_course_file,
    get_assignment_details,
    get_course_context_snapshot,
    get_course_grade_summary,
    get_course_overview,
    get_course_syllabus,
    get_course_tab,
    get_discussion_entries,
    get_today,
    list_announcements,
    list_assignment_groups,
    list_calendar_events,
    list_course_assignments,
    list_course_files,
    list_course_folders,
    list_course_pages,
    list_course_people,
    list_course_submissions,
    list_course_tabs,
    list_courses,
    list_discussion_topics,
    list_modules,
    resolve_canvas_url,
    resolve_course,
)

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler


TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="get_today",
        description="Get today's date in ISO format.",
        parameters={"type": "object", "properties": {}},
        handler=get_today,
    ),
    ToolSpec(
        name="list_courses",
        description="List Canvas courses for the current user.",
        parameters={
            "type": "object",
            "properties": {
                "favorites_only": {
                    "type": "boolean",
                    "description": "Defaults to true.",
                },
                "search": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
        },
        handler=list_courses,
    ),
    ToolSpec(
        name="resolve_course",
        description="Resolve a natural-language course query to likely Canvas courses.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "favorites_only": {
                    "type": "boolean",
                    "description": "Defaults to true.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["query"],
        },
        handler=resolve_course,
    ),
    ToolSpec(
        name="get_course_overview",
        description="Get overview metadata for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
            },
            "required": ["course_id"],
        },
        handler=get_course_overview,
    ),
    ToolSpec(
        name="get_course_syllabus",
        description="Get syllabus metadata and optional syllabus body.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "include_body": {"type": "boolean"},
                "body_char_limit": {
                    "type": "integer",
                    "minimum": 200,
                    "maximum": 200000,
                },
            },
            "required": ["course_id"],
        },
        handler=get_course_syllabus,
    ),
    ToolSpec(
        name="list_course_assignments",
        description="List assignments for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "search": {"type": "string"},
                "bucket": {
                    "type": "string",
                    "enum": [
                        "past",
                        "overdue",
                        "undated",
                        "ungraded",
                        "unsubmitted",
                        "upcoming",
                        "future",
                    ],
                },
                "include_submission": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_assignments,
    ),
    ToolSpec(
        name="get_assignment_details",
        description="Get full details for a single assignment in a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "assignment_id": {"type": "string"},
                "include_submission": {"type": "boolean"},
            },
            "required": ["course_id", "assignment_id"],
        },
        handler=get_assignment_details,
    ),
    ToolSpec(
        name="list_course_pages",
        description="List pages in a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "search": {"type": "string"},
                "published_only": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_pages,
    ),
    ToolSpec(
        name="list_course_tabs",
        description="List navigation tabs in a course (left sidebar entries).",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_tabs,
    ),
    ToolSpec(
        name="get_course_tab",
        description=(
            "Get one course navigation tab by id and optionally resolve/fetch the tab target."
        ),
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "tab_id": {"type": "string"},
                "include_target": {"type": "boolean"},
            },
            "required": ["course_id", "tab_id"],
        },
        handler=get_course_tab,
    ),
    ToolSpec(
        name="list_discussion_topics",
        description="List discussion topics in a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "search": {"type": "string"},
                "only_graded": {"type": "boolean"},
                "exact_title": {"type": "boolean"},
                "include_announcements": {"type": "boolean"},
                "search_in": {
                    "type": "string",
                    "enum": ["title", "title_or_message"],
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_discussion_topics,
    ),
    ToolSpec(
        name="get_discussion_entries",
        description="Get discussion entries for a topic in a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "topic_id": {"type": "string"},
                "include_replies": {"type": "boolean"},
                "include_participants": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id", "topic_id"],
        },
        handler=get_discussion_entries,
    ),
    ToolSpec(
        name="list_course_files",
        description="List files for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "search": {"type": "string"},
                "sort": {
                    "type": "string",
                    "enum": [
                        "name",
                        "size",
                        "created_at",
                        "updated_at",
                        "content_type",
                        "user",
                    ],
                },
                "order": {"type": "string", "enum": ["asc", "desc"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_files,
    ),
    ToolSpec(
        name="download_course_file",
        description="Download a course file into local temp storage and return the local path.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "file_id": {"type": "string"},
                "force_refresh": {"type": "boolean"},
            },
            "required": ["course_id", "file_id"],
        },
        handler=download_course_file,
    ),
    ToolSpec(
        name="list_course_folders",
        description="List folders for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_folders,
    ),
    ToolSpec(
        name="list_assignment_groups",
        description="List assignment groups for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "include_assignments": {"type": "boolean"},
                "include_submission": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_assignment_groups,
    ),
    ToolSpec(
        name="list_course_submissions",
        description="List submissions for a student in a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "student_id": {"type": "string"},
                "assignment_ids": {"type": "array", "items": {"type": "string"}},
                "include": {"type": "array", "items": {"type": "string"}},
                "grouped": {"type": "boolean"},
                "workflow_state": {"type": "string"},
                "submitted_since": {"type": "string", "description": "ISO datetime."},
                "graded_since": {"type": "string", "description": "ISO datetime."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_submissions,
    ),
    ToolSpec(
        name="get_course_grade_summary",
        description="Get grade summary and group-level performance for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "student_id": {"type": "string"},
            },
            "required": ["course_id"],
        },
        handler=get_course_grade_summary,
    ),
    ToolSpec(
        name="list_modules",
        description="List modules for a course, optionally including module items.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "search": {"type": "string"},
                "include_items": {"type": "boolean"},
                "include_content_details": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
                "items_limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_modules,
    ),
    ToolSpec(
        name="canvas_get_page",
        description="Get a course wiki page by page URL slug or page ID.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "url_or_id": {"type": "string"},
                "force_as_id": {"type": "boolean"},
            },
            "required": ["course_id", "url_or_id"],
        },
        handler=canvas_get_page,
    ),
    ToolSpec(
        name="list_announcements",
        description="List announcements for one or more courses.",
        parameters={
            "type": "object",
            "properties": {
                "course_ids": {"type": "array", "items": {"type": "string"}},
                "start_date": {"type": "string", "description": "ISO datetime."},
                "end_date": {"type": "string", "description": "ISO datetime."},
                "active_only": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_ids"],
        },
        handler=list_announcements,
    ),
    ToolSpec(
        name="list_calendar_events",
        description="List calendar events and assignments.",
        parameters={
            "type": "object",
            "properties": {
                "course_ids": {"type": "array", "items": {"type": "string"}},
                "type": {"type": "string", "enum": ["event", "assignment", "both"]},
                "start_date": {"type": "string", "description": "ISO datetime."},
                "end_date": {"type": "string", "description": "ISO datetime."},
                "all_events": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
        },
        handler=list_calendar_events,
    ),
    ToolSpec(
        name="list_course_people",
        description="List users in a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "search": {"type": "string"},
                "enrollment_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "teacher",
                            "student",
                            "student_view",
                            "ta",
                            "observer",
                            "designer",
                        ],
                    },
                },
                "include_email": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["course_id"],
        },
        handler=list_course_people,
    ),
    ToolSpec(
        name="resolve_canvas_url",
        description="Resolve a Canvas URL into object identifiers and optional details.",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "fetch_details": {"type": "boolean"},
            },
            "required": ["url"],
        },
        handler=resolve_canvas_url,
    ),
    ToolSpec(
        name="get_course_context_snapshot",
        description="Get an aggregated context snapshot for a course.",
        parameters={
            "type": "object",
            "properties": {
                "course_id": {"type": "string"},
                "include_syllabus_body": {"type": "boolean"},
                "upcoming_limit": {"type": "integer", "minimum": 1, "maximum": 300},
                "announcements_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 300,
                },
                "modules_limit": {"type": "integer", "minimum": 1, "maximum": 300},
                "module_items_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 300,
                },
            },
            "required": ["course_id"],
        },
        handler=get_course_context_snapshot,
    ),
]

_TOOL_MAP: dict[str, ToolHandler] = {spec.name: spec.handler for spec in TOOL_SPECS}


def dispatch_tool_call(name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    handler = _TOOL_MAP.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}

    try:
        return handler(args or {})
    except CanvasAPIError as exc:
        return {"error": str(exc)}
