from __future__ import annotations

from tools import (
    cancel_scheduled_submission,
    confirm_assignment_submission,
    get_assignment_details,
    get_assignment_rubric,
    get_scheduled_submission,
    install_assignment_submission_files,
    list_assignment_groups,
    list_course_assignments,
    list_course_submissions,
    list_scheduled_submissions,
    preview_assignment_submission,
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
            "include_raw_submission": {
                "type": "boolean",
                "description": "Include the full unfiltered Canvas submission payload per item.",
            },
        },
        required=["course_id"],
    ),
    tool_spec(
        name="install_assignment_submission_files",
        description=(
            "Download attachment files from the current user's submission for one assignment."
        ),
        handler=install_assignment_submission_files,
        properties={
            "course_id": {"type": "string"},
            "assignment_id": {"type": "string"},
            "force_refresh": {"type": "boolean"},
        },
        required=["course_id", "assignment_id"],
    ),
    tool_spec(
        name="preview_assignment_submission",
        description=(
            "Preview an assignment submit or scheduled submit. Does not upload, "
            "submit, or install launchd. Confirm with preview_token."
        ),
        handler=preview_assignment_submission,
        properties={
            "course_id": {"type": "string"},
            "assignment_id": {"type": "string"},
            "submission_type": {
                "type": "string",
                "enum": ["online_upload", "online_text_entry"],
            },
            "file_paths": {"type": "array", "items": {"type": "string"}},
            "body": {"type": "string"},
            "submit_at": {
                "type": "string",
                "description": "ISO-8601 submit time with timezone offset.",
            },
            "minutes_before_due": {"type": "integer", "minimum": 0, "maximum": 10080},
            "now": {
                "type": "boolean",
                "description": "If true, confirm submits immediately (no LaunchAgent).",
            },
        },
        required=["course_id", "assignment_id", "submission_type"],
    ),
    tool_spec(
        name="confirm_assignment_submission",
        description=(
            "Confirm a previewed submit. Uploads files and either submits now "
            "or arms a local scheduled job. Requires a preview_token."
        ),
        handler=confirm_assignment_submission,
        properties={
            "preview_token": {"type": "string"},
            "override": {
                "type": "boolean",
                "description": "Cancel an existing pending job for this assignment.",
            },
            "caffeinate": {
                "type": "boolean",
                "description": "Keep the Mac awake until the scheduled fire finishes. Illegal with now.",
            },
        },
        required=["preview_token"],
    ),
    tool_spec(
        name="list_scheduled_submissions",
        description="List locally scheduled assignment submissions.",
        handler=list_scheduled_submissions,
        properties={
            "status": {
                "type": "string",
                "enum": [
                    "pending",
                    "submitted",
                    "missed",
                    "auth_failed",
                    "failed",
                    "cancelled",
                ],
            },
        },
    ),
    tool_spec(
        name="get_scheduled_submission",
        description="Get one locally scheduled assignment submission job.",
        handler=get_scheduled_submission,
        properties={"job_id": {"type": "string"}},
        required=["job_id"],
    ),
    tool_spec(
        name="cancel_scheduled_submission",
        description=(
            "Cancel a pending scheduled submission: unload launchd, delete "
            "uploaded Canvas files we created, and stop caffeinate."
        ),
        handler=cancel_scheduled_submission,
        properties={"job_id": {"type": "string"}},
        required=["job_id"],
    ),
]
