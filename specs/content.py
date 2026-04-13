from __future__ import annotations

from tools import (
    download_course_file,
    get_discussion_entries,
    list_announcements,
    list_calendar_events,
    list_course_files,
    list_course_folders,
    list_discussion_topics,
)

from specs.schema import ToolSpec, tool_spec

CONTENT_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="list_discussion_topics",
        description="List discussion topics in a course.",
        handler=list_discussion_topics,
        properties={
            "course_id": {"type": "string"},
            "search": {"type": "string"},
            "only_graded": {"type": "boolean"},
            "exact_title": {"type": "boolean"},
            "include_announcements": {"type": "boolean"},
            "search_in": {"type": "string", "enum": ["title", "title_or_message"]},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="get_discussion_entries",
        description="Get discussion entries for a topic in a course.",
        handler=get_discussion_entries,
        properties={
            "course_id": {"type": "string"},
            "topic_id": {"type": "string"},
            "include_replies": {"type": "boolean"},
            "include_participants": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id", "topic_id"],
    ),
    tool_spec(
        name="list_course_files",
        description="List files for a course.",
        handler=list_course_files,
        properties={
            "course_id": {"type": "string"},
            "search": {"type": "string"},
            "sort": {
                "type": "string",
                "enum": ["name", "size", "created_at", "updated_at", "content_type", "user"],
            },
            "order": {"type": "string", "enum": ["asc", "desc"]},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="download_course_file",
        description="Download a course file into local temp storage and return the local path.",
        handler=download_course_file,
        properties={
            "course_id": {"type": "string"},
            "file_id": {"type": "string"},
            "force_refresh": {"type": "boolean"},
        },
        required=["course_id", "file_id"],
    ),
    tool_spec(
        name="list_course_folders",
        description="List folders for a course.",
        handler=list_course_folders,
        properties={
            "course_id": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="list_announcements",
        description="List announcements for one or more courses.",
        handler=list_announcements,
        properties={
            "course_ids": {"type": "array", "items": {"type": "string"}},
            "start_date": {"type": "string", "description": "ISO datetime."},
            "end_date": {"type": "string", "description": "ISO datetime."},
            "active_only": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_ids"],
    ),
    tool_spec(
        name="list_calendar_events",
        description="List calendar events and assignments.",
        handler=list_calendar_events,
        properties={
            "course_ids": {"type": "array", "items": {"type": "string"}},
            "type": {"type": "string", "enum": ["event", "assignment", "both"]},
            "start_date": {"type": "string", "description": "ISO datetime."},
            "end_date": {"type": "string", "description": "ISO datetime."},
            "all_events": {"type": "boolean"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
    ),
]
