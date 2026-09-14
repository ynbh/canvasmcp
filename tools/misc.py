from __future__ import annotations

from datetime import date
from typing import Any

from auth import CanvasAPIError
from tools.common import (
    canvas_client,
    clamp,
    missing_argument,
    parse_canvas_url_path,
    tool_error,
    truncate_html,
)
from tools.resolvers import resolve_canvas_url


def get_today(_: dict[str, Any]) -> dict[str, Any]:
    return {"today": date.today().isoformat()}


def canvas_get_page(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    url_or_id = str(args.get("url_or_id", "")).strip()
    if not course_id:
        return missing_argument("course_id")
    if not url_or_id:
        return missing_argument("url_or_id")

    if "://" in url_or_id:
        _, _, parts = parse_canvas_url_path(url_or_id)
        if len(parts) >= 4 and parts[0] == "courses":
            section = parts[2]
            if section != "pages":
                return tool_error(
                    "unsupported_url_pattern",
                    (
                        "canvas_get_page only supports course wiki page URLs. "
                        "Use resolve_canvas_url to route assignment/discussion/file URLs."
                    ),
                    url=url_or_id,
                    suggested_tool="resolve_canvas_url",
                )
            url_or_id = parts[3]

    page = canvas_client().get_page(
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
        return missing_argument("course_ids")

    limit = clamp(args.get("limit"), 100)
    announcements = canvas_client().list_announcements(
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
            "message": truncate_html(item.get("message")),
        }
        for item in announcements
    ]
    return {"course_ids": course_ids, "count": len(items), "announcements": items}


def list_todo_items(args: dict[str, Any]) -> dict[str, Any]:
    raw_course_ids = args.get("course_ids") or []
    course_ids = [
        str(course_id).strip() for course_id in raw_course_ids if str(course_id).strip()
    ]
    limit = clamp(args.get("limit"), 100)
    todo_items = canvas_client().list_todo_items(
        course_ids=course_ids or None,
        limit=limit,
    )
    items = [
        {
            "type": item.get("type"),
            "course_id": str(item.get("course_id", "")),
            "context_name": item.get("context_name"),
            "context_type": item.get("context_type"),
            "html_url": item.get("html_url"),
            "ignore": bool(item.get("ignore", False)),
            "ignore_permanently": bool(item.get("ignore_permanently", False)),
            "assignment": _map_todo_assignment(item.get("assignment") or {}),
        }
        for item in todo_items
    ]
    return {"course_ids": course_ids, "count": len(items), "todo": items}


def _map_todo_assignment(assignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(assignment.get("id", "")),
        "name": assignment.get("name"),
        "due_at": assignment.get("due_at"),
        "points_possible": assignment.get("points_possible"),
        "submission_types": assignment.get("submission_types"),
        "html_url": assignment.get("html_url"),
    }


def get_course_context_snapshot(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return missing_argument("course_id")

    include_syllabus_body = bool(args.get("include_syllabus_body", False))
    upcoming_limit = clamp(args.get("upcoming_limit"), 20)
    announcements_limit = clamp(args.get("announcements_limit"), 10)
    modules_limit = clamp(args.get("modules_limit"), 20)
    module_items_limit = clamp(args.get("module_items_limit"), 50)

    from tools.assignments import list_course_assignments
    from tools.courses import get_course_overview, get_course_syllabus
    from tools.files import list_modules
    from tools.grades import get_course_grade_summary

    snapshot: dict[str, Any] = {"course_id": course_id}
    errors: list[dict[str, str]] = []

    try:
        snapshot["overview"] = get_course_overview({"course_id": course_id})
    except CanvasAPIError as exc:
        errors.append({"section": "overview", "error": str(exc)})
    try:
        snapshot["syllabus"] = get_course_syllabus(
            {
                "course_id": course_id,
                "include_body": include_syllabus_body,
                "body_char_limit": 12000,
            }
        )
    except CanvasAPIError as exc:
        errors.append({"section": "syllabus", "error": str(exc)})
    try:
        snapshot["upcoming_assignments"] = list_course_assignments(
            {
                "course_id": course_id,
                "bucket": "upcoming",
                "include_submission": True,
                "limit": upcoming_limit,
            }
        )
    except CanvasAPIError as exc:
        errors.append({"section": "upcoming_assignments", "error": str(exc)})
    try:
        snapshot["announcements"] = list_announcements(
            {
                "course_ids": [course_id],
                "active_only": True,
                "limit": announcements_limit,
            }
        )
    except CanvasAPIError as exc:
        errors.append({"section": "announcements", "error": str(exc)})
    try:
        snapshot["modules"] = list_modules(
            {
                "course_id": course_id,
                "include_items": True,
                "include_content_details": True,
                "limit": modules_limit,
                "items_limit": module_items_limit,
            }
        )
    except CanvasAPIError as exc:
        errors.append({"section": "modules", "error": str(exc)})
    try:
        snapshot["grade_summary"] = get_course_grade_summary({"course_id": course_id})
    except CanvasAPIError as exc:
        errors.append({"section": "grade_summary", "error": str(exc)})

    snapshot["errors"] = errors
    return snapshot
