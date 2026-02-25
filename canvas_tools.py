from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import getpass
from pathlib import Path
import re
import tempfile
from typing import Any, Callable

from canvas_api import CanvasAPIError, create_canvas_client_from_env

MAX_TOOL_LIMIT = 300


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    cleaned = "".join(
        ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text
    )
    return " ".join(cleaned.split())


def _clamp(value: int | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(parsed, MAX_TOOL_LIMIT))


def _download_dir() -> Path:
    username = re.sub(r"[^A-Za-z0-9._-]+", "_", getpass.getuser()).strip("._")
    if not username:
        username = "user"
    return Path(tempfile.gettempdir()) / f"canvas_files_{username}"


def _safe_filename(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    if not sanitized:
        return "canvas_file"
    return sanitized[:180]


def _download_file_path(
    download_dir: Path, course_id: str, file_id: str, filename: str
) -> Path:
    return (
        download_dir / f"course-{course_id}_file-{file_id}_{_safe_filename(filename)}"
    )


@lru_cache(maxsize=1)
def _canvas_client():
    return create_canvas_client_from_env()


def _map_course(course: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(course.get("id", "")),
        "name": str(course.get("name", "Untitled course")),
        "course_code": str(course["course_code"])
        if course.get("course_code")
        else None,
        "term_name": str(course["term"]["name"])
        if isinstance(course.get("term"), dict) and course["term"].get("name")
        else None,
        "state": str(course["workflow_state"])
        if course.get("workflow_state")
        else None,
    }


def _relevance_score(query: str, course: dict[str, Any]) -> float:
    q = _normalize(query)
    if not q:
        return 0.0

    name = _normalize(course.get("name"))
    code = _normalize(course.get("course_code"))

    if q == name or q == code:
        return 1.0

    score = 0.0
    if code.startswith(q):
        score = max(score, 0.97)
    elif q in code:
        score = max(score, 0.91)

    if name.startswith(q):
        score = max(score, 0.93)
    elif q in name:
        score = max(score, 0.86)

    q_tokens = [token for token in q.split(" ") if token]
    if q_tokens:
        overlap = sum(1 for token in q_tokens if token in name or token in code)
        score = max(score, (overlap / len(q_tokens)) * 0.8)

    return score


def get_today(_: dict[str, Any]) -> dict[str, Any]:
    return {"today": date.today().isoformat()}


def list_courses(args: dict[str, Any]) -> dict[str, Any]:
    favorites_only = bool(args.get("favorites_only", True))
    search = args.get("search")
    limit = _clamp(args.get("limit"), 50)
    courses = _canvas_client().list_courses(
        favorites_only=favorites_only,
        search=str(search) if search else None,
        limit=limit,
    )
    mapped = [_map_course(course) for course in courses]
    return {
        "source": "favorites" if favorites_only else "active-enrollments",
        "count": len(mapped),
        "courses": mapped,
    }


def resolve_course(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get("query", "")).strip()
    if not query:
        return {"count": 0, "matches": []}

    favorites_only = bool(args.get("favorites_only", True))
    limit = _clamp(args.get("limit"), 5)

    courses = _canvas_client().list_courses(
        favorites_only=favorites_only,
        limit=200,
    )
    scored = sorted(
        (
            {
                **_map_course(course),
                "score": _relevance_score(query, course),
            }
            for course in courses
        ),
        key=lambda row: row["score"],
        reverse=True,
    )
    matches = [row for row in scored if row["score"] > 0][:limit]
    return {"count": len(matches), "matches": matches}


def list_course_assignments(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = _clamp(args.get("limit"), 100)
    assignments = _canvas_client().list_assignments(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        bucket=str(args.get("bucket")) if args.get("bucket") else None,
        include_submission=bool(args.get("include_submission", False)),
        limit=limit,
    )
    items = [
        {
            "id": str(assignment.get("id", "")),
            "name": str(assignment.get("name", "Untitled assignment")),
            "due_at": assignment.get("due_at"),
            "unlock_at": assignment.get("unlock_at"),
            "lock_at": assignment.get("lock_at"),
            "points_possible": assignment.get("points_possible"),
            "html_url": assignment.get("html_url"),
            "submission_types": assignment.get("submission_types") or [],
        }
        for assignment in assignments
    ]
    return {"course_id": course_id, "count": len(items), "assignments": items}


def get_assignment_details(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not assignment_id:
        return {"error": "assignment_id is required"}

    assignment = _canvas_client().get_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        include_submission=bool(args.get("include_submission", False)),
    )

    return {
        "course_id": course_id,
        "assignment": {
            "id": str(assignment.get("id", "")),
            "name": assignment.get("name", "Untitled assignment"),
            "description": assignment.get("description"),
            "due_at": assignment.get("due_at"),
            "unlock_at": assignment.get("unlock_at"),
            "lock_at": assignment.get("lock_at"),
            "points_possible": assignment.get("points_possible"),
            "html_url": assignment.get("html_url"),
            "published": assignment.get("published"),
            "submission_types": assignment.get("submission_types") or [],
            "grading_type": assignment.get("grading_type"),
            "allowed_extensions": assignment.get("allowed_extensions") or [],
            "has_submitted_submissions": assignment.get("has_submitted_submissions"),
            "submission": assignment.get("submission"),
        },
    }


def list_course_files(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = _clamp(args.get("limit"), 100)
    files = _canvas_client().list_files(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        sort=str(args.get("sort")) if args.get("sort") else None,
        order=str(args.get("order")) if args.get("order") else None,
        limit=limit,
    )
    items = [
        {
            "id": str(file.get("id", "")),
            "display_name": file.get("display_name"),
            "filename": file.get("filename"),
            "content_type": file.get("content_type"),
            "size": file.get("size"),
            "updated_at": file.get("updated_at"),
            "url": file.get("url"),
            "folder_id": str(file["folder_id"])
            if file.get("folder_id") is not None
            else None,
        }
        for file in files
    ]
    return {"course_id": course_id, "count": len(items), "files": items}


def download_course_file(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    file_id = str(args.get("file_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not file_id:
        return {"error": "file_id is required"}

    force_refresh = bool(args.get("force_refresh", False))

    download_dir = _download_dir()
    download_dir.mkdir(parents=True, exist_ok=True)

    file_info = _canvas_client().get_file(course_id=course_id, file_id=file_id)
    display_name = str(
        file_info.get("display_name") or file_info.get("filename") or f"file_{file_id}"
    )
    download_path = _download_file_path(download_dir, course_id, file_id, display_name)

    if download_path.exists() and force_refresh:
        download_path.unlink()

    if download_path.exists():
        return {
            "course_id": course_id,
            "file_id": file_id,
            "display_name": display_name,
            "local_path": str(download_path),
            "size_bytes": download_path.stat().st_size,
            "content_type": file_info.get("content_type"),
            "already_present": True,
        }

    downloaded = _canvas_client().download_file(
        course_id=course_id,
        file_id=file_id,
        destination_path=str(download_path),
    )
    return {
        "course_id": course_id,
        "file_id": file_id,
        "display_name": display_name,
        "local_path": str(download_path),
        "size_bytes": download_path.stat().st_size,
        "content_type": downloaded.get("content_type"),
        "already_present": False,
    }


def list_course_folders(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = _clamp(args.get("limit"), 150)
    folders = _canvas_client().list_folders(course_id=course_id, limit=limit)
    items = [
        {
            "id": str(folder.get("id", "")),
            "name": folder.get("name", "Untitled folder"),
            "full_name": folder.get("full_name"),
            "parent_folder_id": str(folder["parent_folder_id"])
            if folder.get("parent_folder_id") is not None
            else None,
            "files_count": folder.get("files_count"),
            "folders_count": folder.get("folders_count"),
            "updated_at": folder.get("updated_at"),
        }
        for folder in folders
    ]
    return {"course_id": course_id, "count": len(items), "folders": items}


def list_modules(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = _clamp(args.get("limit"), 100)
    items_limit = _clamp(args.get("items_limit"), 100)
    modules = _canvas_client().list_modules(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        include_items=bool(args.get("include_items", False)),
        include_content_details=bool(args.get("include_content_details", False)),
        limit=limit,
        items_limit=items_limit,
    )

    items = []
    for module in modules:
        module_items = []
        if isinstance(module.get("items"), list):
            module_items = [
                {
                    "id": str(item.get("id", "")),
                    "type": item.get("type"),
                    "title": item.get("title"),
                    "page_url": item.get("page_url"),
                    "content_id": str(item["content_id"])
                    if item.get("content_id") is not None
                    else None,
                    "html_url": item.get("html_url"),
                    "url": item.get("url"),
                    "published": item.get("published"),
                    "position": item.get("position"),
                    "completion_requirement": item.get("completion_requirement"),
                    "content_details": item.get("content_details"),
                }
                for item in module["items"]
                if isinstance(item, dict)
            ]

        items.append(
            {
                "id": str(module.get("id", "")),
                "name": module.get("name", "Untitled module"),
                "position": module.get("position"),
                "unlock_at": module.get("unlock_at"),
                "require_sequential_progress": module.get(
                    "require_sequential_progress"
                ),
                "publish_final_grade": module.get("publish_final_grade"),
                "published": module.get("published"),
                "state": module.get("state"),
                "prerequisite_module_ids": [
                    str(module_id)
                    for module_id in (module.get("prerequisite_module_ids") or [])
                ],
                "items_count": module.get("items_count"),
                "items_url": module.get("items_url"),
                "items": module_items,
            }
        )

    return {"course_id": course_id, "count": len(items), "modules": items}


def canvas_get_page(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    url_or_id = str(args.get("url_or_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not url_or_id:
        return {"error": "url_or_id is required"}

    page = _canvas_client().get_page(
        course_id=course_id,
        url_or_id=url_or_id,
        force_as_id=bool(args.get("force_as_id", False)),
    )
    page_id = page.get("page_id")
    if page_id is None and page.get("id") is not None:
        page_id = page.get("id")

    return {
        "course_id": course_id,
        "requested": {
            "url_or_id": url_or_id,
            "force_as_id": bool(args.get("force_as_id", False)),
        },
        "page": {
            "page_id": str(page_id) if page_id is not None else None,
            "url": page.get("url"),
            "title": page.get("title"),
            "created_at": page.get("created_at"),
            "updated_at": page.get("updated_at"),
            "published": page.get("published"),
            "front_page": page.get("front_page"),
            "hide_from_students": page.get("hide_from_students"),
            "editing_roles": page.get("editing_roles"),
            "html_url": page.get("html_url"),
            "body": page.get("body"),
            "lock_info": page.get("lock_info"),
            "locked_for_user": page.get("locked_for_user"),
        },
    }


def list_announcements(args: dict[str, Any]) -> dict[str, Any]:
    raw_course_ids = args.get("course_ids") or []
    course_ids = [
        str(course_id).strip() for course_id in raw_course_ids if str(course_id).strip()
    ]
    if not course_ids:
        return {"error": "course_ids is required"}

    limit = _clamp(args.get("limit"), 100)
    announcements = _canvas_client().list_announcements(
        course_ids=course_ids,
        start_date=str(args.get("start_date")) if args.get("start_date") else None,
        end_date=str(args.get("end_date")) if args.get("end_date") else None,
        active_only=bool(args.get("active_only", True)),
        limit=limit,
    )
    items = [
        {
            "id": str(item.get("id", "")),
            "title": item.get("title", "Untitled announcement"),
            "posted_at": item.get("posted_at"),
            "context_code": item.get("context_code"),
            "html_url": item.get("html_url"),
            "message": item.get("message"),
        }
        for item in announcements
    ]
    return {"course_ids": course_ids, "count": len(items), "announcements": items}


def list_calendar_events(args: dict[str, Any]) -> dict[str, Any]:
    raw_course_ids = args.get("course_ids") or []
    course_ids = [
        str(course_id).strip() for course_id in raw_course_ids if str(course_id).strip()
    ]
    limit = _clamp(args.get("limit"), 100)

    events = _canvas_client().list_calendar_events(
        course_ids=course_ids or None,
        event_type=str(args.get("type")) if args.get("type") else None,
        start_date=str(args.get("start_date")) if args.get("start_date") else None,
        end_date=str(args.get("end_date")) if args.get("end_date") else None,
        all_events=bool(args.get("all_events")) if "all_events" in args else None,
        limit=limit,
    )
    items = [
        {
            "id": str(event.get("id", "")),
            "title": event.get("title", "Untitled event"),
            "context_code": event.get("context_code"),
            "type": event.get("type"),
            "start_at": event.get("start_at"),
            "end_at": event.get("end_at"),
            "all_day": bool(event.get("all_day")),
            "html_url": event.get("html_url"),
        }
        for event in events
    ]
    return {"course_ids": course_ids, "count": len(items), "events": items}


def list_course_people(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    enrollment_types = args.get("enrollment_types")
    if enrollment_types is not None and not isinstance(enrollment_types, list):
        return {"error": "enrollment_types must be an array of strings"}

    limit = _clamp(args.get("limit"), 100)
    users = _canvas_client().list_course_users(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        enrollment_types=[str(item) for item in enrollment_types]
        if enrollment_types
        else None,
        include_email=bool(args.get("include_email", True)),
        limit=limit,
    )
    people = [
        {
            "id": str(user.get("id", "")),
            "name": user.get("name", "Unknown user"),
            "sortable_name": user.get("sortable_name"),
            "short_name": user.get("short_name"),
            "email": user.get("email"),
            "avatar_url": user.get("avatar_url"),
            "enrollments": [
                {
                    "type": enrollment.get("type"),
                    "role": enrollment.get("role"),
                    "enrollment_state": enrollment.get("enrollment_state"),
                }
                for enrollment in (user.get("enrollments") or [])
                if isinstance(enrollment, dict)
            ],
        }
        for user in users
    ]
    return {"course_id": course_id, "count": len(people), "people": people}


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
