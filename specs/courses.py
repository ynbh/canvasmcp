from __future__ import annotations

from tools import (
    canvas_get_page,
    get_course_context_snapshot,
    get_course_grade_summary,
    get_course_overview,
    get_course_syllabus,
    get_course_tab,
    list_course_pages,
    list_course_people,
    list_course_tabs,
    list_modules,
    resolve_canvas_url,
)

from specs.schema import ToolSpec, tool_spec

COURSE_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="get_course_overview",
        description="Get overview metadata for a course.",
        handler=get_course_overview,
        properties={"course_id": {"type": "string"}},
        required=["course_id"],
    ),
    tool_spec(
        name="get_course_syllabus",
        description="Get syllabus metadata and optional syllabus body.",
        handler=get_course_syllabus,
        properties={
            "course_id": {"type": "string"},
            "include_body": {"type": "boolean"},
            "body_char_limit": {"type": "integer", "minimum": 200, "maximum": 200000},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="list_course_pages",
        description="List pages in a course.",
        handler=list_course_pages,
        properties={
            "course_id": {"type": "string"},
            "search": {"type": "string"},
            "published_only": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="canvas_get_page",
        description="Get a course wiki page by page URL slug or page ID.",
        handler=canvas_get_page,
        properties={
            "course_id": {"type": "string"},
            "url_or_id": {"type": "string"},
            "force_as_id": {"type": "boolean"},
        },
        required=["course_id", "url_or_id"],
    ),
    tool_spec(
        name="list_course_tabs",
        description="List navigation tabs in a course (left sidebar entries).",
        handler=list_course_tabs,
        properties={
            "course_id": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="get_course_tab",
        description="Get one course navigation tab by id and optionally resolve/fetch the tab target.",
        handler=get_course_tab,
        properties={
            "course_id": {"type": "string"},
            "tab_id": {"type": "string"},
            "include_target": {"type": "boolean"},
        },
        required=["course_id", "tab_id"],
    ),
    tool_spec(
        name="list_course_people",
        description="List users in a course.",
        handler=list_course_people,
        properties={
            "course_id": {"type": "string"},
            "search": {"type": "string"},
            "enrollment_types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["teacher", "student", "student_view", "ta", "observer", "designer"],
                },
            },
            "include_email": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="list_modules",
        description="List modules for a course, optionally including module items.",
        handler=list_modules,
        properties={
            "course_id": {"type": "string"},
            "search": {"type": "string"},
            "include_items": {"type": "boolean"},
            "include_content_details": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
            "items_limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="get_course_grade_summary",
        description="Get grade summary and group-level performance for a course.",
        handler=get_course_grade_summary,
        properties={"course_id": {"type": "string"}, "student_id": {"type": "string"}},
        required=["course_id"],
    ),
    tool_spec(
        name="resolve_canvas_url",
        description="Resolve a Canvas URL into object identifiers and optional details.",
        handler=resolve_canvas_url,
        properties={"url": {"type": "string"}, "fetch_details": {"type": "boolean"}},
        required=["url"],
    ),
    tool_spec(
        name="get_course_context_snapshot",
        description="Get an aggregated context snapshot for a course.",
        handler=get_course_context_snapshot,
        properties={
            "course_id": {"type": "string"},
            "include_syllabus_body": {"type": "boolean"},
            "upcoming_limit": {"type": "integer", "minimum": 1, "maximum": 300},
            "announcements_limit": {"type": "integer", "minimum": 1, "maximum": 300},
            "modules_limit": {"type": "integer", "minimum": 1, "maximum": 300},
            "module_items_limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
]
