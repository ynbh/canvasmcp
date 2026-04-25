from __future__ import annotations

from datetime import date
from typing import Any

from auth import CanvasAPIError
from tools.common import (
    candidate_ids_for_lookup,
    canvas_client,
    clamp,
    expand_canvas_id,
    id_aliases,
    parse_canvas_course_resource,
    parse_canvas_url_path,
    recommended_tool_for_resource,
)


def get_today(_: dict[str, Any]) -> dict[str, Any]:
    return {"today": date.today().isoformat()}


def canvas_get_page(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    url_or_id = str(args.get("url_or_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not url_or_id:
        return {"error": "url_or_id is required"}

    if "://" in url_or_id:
        _, _, parts = parse_canvas_url_path(url_or_id)
        if len(parts) >= 4 and parts[0] == "courses":
            section = parts[2]
            if section != "pages":
                return {
                    "error": "unsupported_url_pattern",
                    "message": (
                        "canvas_get_page only supports course wiki page URLs. "
                        "Use resolve_canvas_url to route assignment/discussion/file URLs."
                    ),
                    "url": url_or_id,
                    "suggested_tool": "resolve_canvas_url",
                }
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
        return {"error": "course_ids is required"}

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
    limit = clamp(args.get("limit"), 100)
    events = canvas_client().list_calendar_events(
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


def resolve_canvas_resource_details(
    *,
    course_id: str,
    resource_type: str,
    resource_id: str | None,
    resource_id_raw: str | None,
) -> dict[str, Any] | None:
    from tools.assignments import (
        get_assignment_details,
    )
    from tools.courses import (
        get_course_overview,
        get_course_syllabus,
        list_course_pages,
        list_course_people,
    )
    from tools.discussions import get_discussion_entries, list_discussion_topics
    from tools.grades import get_course_grade_summary
    from tools.submissions import list_course_submissions

    if resource_type == "course":
        return get_course_overview({"course_id": course_id})
    if resource_type == "front_page":
        page = canvas_client().get_front_page(course_id=course_id)
        return {
            "course_id": course_id,
            "page": {
                "page_id": str(page.get("page_id", "")),
                "url": page.get("url"),
                "title": page.get("title"),
                "html_url": page.get("html_url"),
                "body": page.get("body"),
            },
        }
    if resource_type == "syllabus":
        return get_course_syllabus({"course_id": course_id, "include_body": True})
    if resource_type == "course_grades":
        return get_course_grade_summary({"course_id": course_id})
    if resource_type == "course_people":
        return list_course_people({"course_id": course_id, "limit": 100})
    if resource_type == "discussion_topics_index":
        return list_discussion_topics({"course_id": course_id, "limit": 100})
    if resource_type == "pages_index":
        return list_course_pages({"course_id": course_id, "limit": 100})
    if resource_type == "assignment" and resource_id:
        for candidate in candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                assignment = canvas_client().get_assignment(
                    course_id=course_id,
                    assignment_id=candidate,
                    include_submission=False,
                )
                return {
                    "course_id": course_id,
                    "assignment": {
                        "id": str(assignment.get("id", "")),
                        "name": assignment.get("name"),
                        "due_at": assignment.get("due_at"),
                        "points_possible": assignment.get("points_possible"),
                        "html_url": assignment.get("html_url"),
                    },
                }
            except CanvasAPIError:
                continue
        return None
    if resource_type == "discussion_topic" and resource_id:
        for candidate in candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                view = canvas_client().get_discussion_topic_view(
                    course_id=course_id,
                    topic_id=candidate,
                )
                return {
                    "course_id": course_id,
                    "topic": {
                        "id": str(view.get("id", "")),
                        "title": view.get("title"),
                        "html_url": view.get("html_url"),
                    },
                }
            except CanvasAPIError:
                continue
        return None
    if resource_type == "page" and resource_id_raw:
        page = canvas_client().get_page(
            course_id=course_id,
            url_or_id=resource_id_raw,
            force_as_id=False,
        )
        return {
            "course_id": course_id,
            "page": {
                "page_id": str(page.get("page_id", "")),
                "url": page.get("url"),
                "title": page.get("title"),
                "html_url": page.get("html_url"),
            },
        }
    if resource_type == "file" and resource_id:
        for candidate in candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                file_info = canvas_client().get_file(
                    course_id=course_id,
                    file_id=candidate,
                )
                return {
                    "course_id": course_id,
                    "file": {
                        "id": str(file_info.get("id", "")),
                        "display_name": file_info.get("display_name"),
                        "filename": file_info.get("filename"),
                        "size": file_info.get("size"),
                        "url": file_info.get("url"),
                    },
                }
            except CanvasAPIError:
                continue
        return None
    if resource_type == "assignment_submission":
        return list_course_submissions({"course_id": course_id, "limit": 200})
    if resource_type == "discussion_topic":
        return get_discussion_entries({"course_id": course_id, "topic_id": resource_id or ""})
    if resource_type == "assignment":
        return get_assignment_details({"course_id": course_id, "assignment_id": resource_id or ""})
    return None


def resolve_canvas_url(args: dict[str, Any]) -> dict[str, Any]:
    url = str(args.get("url", "")).strip()
    if not url:
        return {"error": "url is required"}

    parsed, path, parts = parse_canvas_url_path(url)
    course_id_raw, resource_type, resource_id_raw = parse_canvas_course_resource(parts)
    course_id = str(course_id_raw).strip() if course_id_raw else None
    resource_id = (
        expand_canvas_id(resource_id_raw, course_id=course_id) if resource_id_raw else None
    )
    recommended_tool = recommended_tool_for_resource(resource_type)

    fetch_details = bool(args.get("fetch_details", True))
    details: dict[str, Any] | None = None
    detail_error: str | None = None
    if fetch_details and course_id and resource_type:
        try:
            details = resolve_canvas_resource_details(
                course_id=course_id,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_id_raw=resource_id_raw,
            )
        except CanvasAPIError as exc:
            detail_error = str(exc)

    return {
        "url": url,
        "domain": parsed.netloc,
        "path": path,
        "course_id_raw": course_id_raw,
        "course_id": course_id,
        "course_id_aliases": id_aliases(course_id_raw or "", course_id=course_id),
        "resource_type": resource_type,
        "resource_id_raw": resource_id_raw,
        "resource_id": resource_id,
        "resource_id_aliases": id_aliases(resource_id_raw or "", course_id=course_id),
        "recommended_tool": recommended_tool,
        "details": details,
        "detail_error": detail_error,
    }


def get_course_context_snapshot(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

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
