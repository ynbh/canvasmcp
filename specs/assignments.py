from __future__ import annotations

from tools import (
    get_assignment_details,
    get_assignment_rubric,
    list_assignment_groups,
    list_course_assignments,
    list_course_submissions,
)

from specs.schema import ToolSpec, tool_spec

ASSIGNMENT_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="list_course_assignments",
        description="List assignments for a course.",
        handler=list_course_assignments,
        properties={
            "course_id": {"type": "string"},
            "search": {"type": "string"},
            "bucket": {
                "type": "string",
                "enum": ["past", "overdue", "undated", "ungraded", "unsubmitted", "upcoming", "future"],
            },
            "include_submission": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="get_assignment_details",
        description=(
            "Get full details for a single assignment in a course, including rubric "
            "fields when Canvas returns them."
        ),
        handler=get_assignment_details,
        properties={
            "course_id": {"type": "string"},
            "assignment_id": {"type": "string"},
            "include_submission": {"type": "boolean"},
        },
        required=["course_id", "assignment_id"],
    ),
    tool_spec(
        name="get_assignment_rubric",
        description="Get the rubric criteria/settings for a single assignment.",
        handler=get_assignment_rubric,
        properties={
            "course_id": {"type": "string"},
            "assignment_id": {"type": "string"},
            "include_assessment": {
                "type": "boolean",
                "description": "Include the current user's rubric assessment when available.",
            },
        },
        required=["course_id", "assignment_id"],
    ),
    tool_spec(
        name="list_assignment_groups",
        description="List assignment groups for a course.",
        handler=list_assignment_groups,
        properties={
            "course_id": {"type": "string"},
            "include_assignments": {"type": "boolean"},
            "include_submission": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="list_course_submissions",
        description="List submissions for a student in a course.",
        handler=list_course_submissions,
        properties={
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
        required=["course_id"],
    ),
]
