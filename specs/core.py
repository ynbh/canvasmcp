from __future__ import annotations

from tools import get_today, list_courses, resolve_course

from specs.schema import ToolSpec, tool_spec

CORE_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="get_today",
        description="Get today's date in ISO format.",
        handler=get_today,
    ),
    tool_spec(
        name="list_courses",
        description="List Canvas courses for the current user.",
        handler=list_courses,
        properties={
            "favorites_only": {"type": "boolean", "description": "Defaults to true."},
            "search": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
    ),
    tool_spec(
        name="resolve_course",
        description="Resolve a natural-language course query to likely Canvas courses.",
        handler=resolve_course,
        properties={
            "query": {"type": "string"},
            "favorites_only": {"type": "boolean", "description": "Defaults to true."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 20},
        },
        required=["query"],
    ),
]
