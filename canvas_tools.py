from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import getpass
from pathlib import Path
import re
import tempfile
from typing import Any, Callable
from urllib.parse import unquote, urlparse

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


def _map_course_tab(tab: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(tab.get("id", "")),
        "label": tab.get("label"),
        "type": tab.get("type"),
        "position": tab.get("position"),
        "hidden": tab.get("hidden"),
        "visibility": tab.get("visibility"),
        "url": tab.get("url"),
        "full_url": tab.get("full_url"),
        "html_url": tab.get("html_url"),
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


def _course_id_prefix(course_id: str | None) -> str | None:
    if not course_id:
        return None
    trimmed = str(course_id).strip()
    if not trimmed:
        return None
    tilde_match = re.fullmatch(r"(\d+)~(\d+)", trimmed)
    if tilde_match:
        return tilde_match.group(1)
    full_match = re.fullmatch(r"(\d+)000000(\d+)", trimmed)
    if full_match:
        return full_match.group(1)
    if trimmed.isdigit() and len(trimmed) >= 4:
        return trimmed[:4]
    return None


def _expand_canvas_id(raw_id: str, *, course_id: str | None = None) -> str:
    trimmed = str(raw_id).strip()
    if not trimmed:
        return trimmed

    tilde_match = re.fullmatch(r"(\d+)~(\d+)", trimmed)
    if tilde_match:
        return f"{tilde_match.group(1)}000000{tilde_match.group(2)}"

    if not trimmed.isdigit():
        return trimmed

    if "000000" in trimmed:
        return trimmed

    prefix = _course_id_prefix(course_id)
    if prefix:
        return f"{prefix}000000{trimmed}"

    return trimmed


def _collapse_canvas_id(raw_id: str) -> str:
    match = re.fullmatch(r"(\d+)000000(\d+)", raw_id.strip())
    if not match:
        return raw_id
    return f"{match.group(1)}~{match.group(2)}"


def _short_canvas_id(raw_id: str) -> str:
    match = re.fullmatch(r"(\d+)000000(\d+)", raw_id.strip())
    if match:
        return match.group(2)
    tilde_match = re.fullmatch(r"(\d+)~(\d+)", raw_id.strip())
    if tilde_match:
        return tilde_match.group(2)
    return raw_id.strip()


def _id_aliases(raw_id: str, *, course_id: str | None = None) -> list[str]:
    trimmed = str(raw_id).strip()
    if not trimmed:
        return []

    candidates: list[str] = []
    for value in (
        trimmed,
        _expand_canvas_id(trimmed, course_id=course_id),
        _collapse_canvas_id(_expand_canvas_id(trimmed, course_id=course_id)),
        _short_canvas_id(_expand_canvas_id(trimmed, course_id=course_id)),
    ):
        if value and value not in candidates:
            candidates.append(value)
    return candidates


def _candidate_ids_for_lookup(
    raw_id: str, *, course_id: str | None = None
) -> list[str]:
    aliases = _id_aliases(raw_id, course_id=course_id)
    if not aliases:
        return []

    expanded = _expand_canvas_id(raw_id, course_id=course_id)
    ordered: list[str] = []
    for value in [expanded, *aliases]:
        if value and value not in ordered:
            ordered.append(value)
    return ordered


def _extract_discussion_topic_id(item: dict[str, Any]) -> str | None:
    direct = item.get("discussion_topic_id")
    if direct is not None:
        return str(direct)
    topic = item.get("discussion_topic")
    if isinstance(topic, dict) and topic.get("id") is not None:
        return str(topic["id"])
    return None


def _is_announcement_topic(topic: dict[str, Any]) -> bool:
    return bool(
        topic.get("announcement")
        or topic.get("is_announcement")
        or str(topic.get("discussion_type", "")).casefold() == "announcement"
    )


def _assignment_to_discussion_topic(
    assignment: dict[str, Any],
) -> dict[str, Any] | None:
    discussion_topic_id = _extract_discussion_topic_id(assignment)
    if not discussion_topic_id:
        return None

    submission_types = assignment.get("submission_types") or []
    if "discussion_topic" not in submission_types and not assignment.get(
        "discussion_topic"
    ):
        return None

    discussion_topic_raw = assignment.get("discussion_topic")
    has_discussion_topic = isinstance(discussion_topic_raw, dict)
    discussion_topic = discussion_topic_raw if has_discussion_topic else {}
    assignment_title = str(assignment.get("name") or "").strip()

    title = (
        discussion_topic.get("title")
        if has_discussion_topic and discussion_topic.get("title")
        else assignment_title
    )

    html_url = discussion_topic.get("html_url")
    if not html_url:
        html_url = assignment.get("html_url")

    return {
        "id": discussion_topic_id,
        "title": title,
        "message": discussion_topic.get("message")
        if has_discussion_topic
        else assignment.get("description"),
        "posted_at": discussion_topic.get("posted_at")
        if has_discussion_topic
        else None,
        "last_reply_at": discussion_topic.get("last_reply_at")
        if has_discussion_topic
        else None,
        "delayed_post_at": discussion_topic.get("delayed_post_at")
        if has_discussion_topic
        else None,
        "lock_at": discussion_topic.get("lock_at")
        if has_discussion_topic
        else assignment.get("lock_at"),
        "discussion_type": discussion_topic.get("discussion_type")
        if has_discussion_topic
        else "threaded",
        "published": discussion_topic.get("published")
        if has_discussion_topic
        else assignment.get("published"),
        "locked": discussion_topic.get("locked") if has_discussion_topic else None,
        "pinned": discussion_topic.get("pinned") if has_discussion_topic else False,
        "assignment_id": str(assignment.get("id", "")),
        "points_possible": assignment.get("points_possible"),
        "html_url": html_url,
        "source": "assignment_linked",
    }


def _is_forbidden_message(message: str) -> bool:
    lowered = message.casefold()
    return (
        "forbidden" in lowered
        or "not authorised" in lowered
        or "not authorized" in lowered
        or "unauthorized" in lowered
    )


def _is_not_found_message(message: str) -> bool:
    lowered = message.casefold()
    return "not found" in lowered or "could not find" in lowered


def _first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _first_non_empty_str(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _course_tab_target_url(tab_id: str, tab: dict[str, Any]) -> str:
    target_url = _first_non_empty_str(
        tab.get("html_url"),
        tab.get("full_url"),
        tab.get("url"),
    )
    if tab_id.strip().lower() == "home" and re.fullmatch(
        r"(?:https?://[^/]+)?/courses/\d+", target_url.rstrip("/")
    ):
        return f"{target_url.rstrip('/')}/home"
    return target_url


def _parse_canvas_course_resource(
    parts: list[str],
) -> tuple[str | None, str | None, str | None]:
    if len(parts) < 2 or parts[0] != "courses":
        return None, None, None

    course_id_raw = parts[1]
    if len(parts) == 2:
        return course_id_raw, "course", parts[1]

    section = parts[2]
    top_level_map = {
        "syllabus": ("syllabus", "syllabus"),
        "home": ("front_page", "front_page"),
        "grades": ("course_grades", "grades"),
        "users": ("course_people", "users"),
    }
    if section in top_level_map:
        resource_type, resource_id_raw = top_level_map[section]
        return course_id_raw, resource_type, resource_id_raw
    if section == "discussion_topics" and len(parts) == 3:
        return course_id_raw, "discussion_topics_index", "discussion_topics"
    if section == "pages" and len(parts) == 3:
        return course_id_raw, "pages_index", "pages"

    if len(parts) >= 4:
        if section == "assignments" and parts[3] == "syllabus":
            return course_id_raw, "syllabus", "syllabus"

        if section in {
            "assignments",
            "discussion_topics",
            "files",
            "quizzes",
            "modules",
            "pages",
            "announcements",
        }:
            resource_type = section[:-1] if section.endswith("s") else section
            resource_id_raw = parts[3]
            if section == "modules" and len(parts) >= 5 and parts[3] == "items":
                return course_id_raw, "module_item", parts[4]
            if (
                section == "assignments"
                and len(parts) >= 6
                and parts[4] == "submissions"
                and parts[5]
            ):
                return course_id_raw, "assignment_submission", parts[3]
            return course_id_raw, resource_type, resource_id_raw

    return course_id_raw, "course_route", parts[2]


def _recommended_tool_for_resource(resource_type: str | None) -> str | None:
    return {
        "assignment": "get_assignment_details",
        "discussion_topic": "get_discussion_entries",
        "discussion_topics_index": "list_discussion_topics",
        "page": "canvas_get_page",
        "pages_index": "list_course_pages",
        "file": "download_course_file",
        "syllabus": "get_course_syllabus",
        "course_grades": "get_course_grade_summary",
        "course_people": "list_course_people",
        "front_page": "get_course_tab",
        "course": "get_course_overview",
        "assignment_submission": "list_course_submissions",
    }.get(resource_type)


def _resolve_canvas_resource_details(
    *,
    course_id: str,
    resource_type: str,
    resource_id: str | None,
    resource_id_raw: str | None,
) -> dict[str, Any] | None:
    if resource_type == "course":
        return get_course_overview({"course_id": course_id})
    if resource_type == "front_page":
        page = _canvas_client().get_front_page(course_id=course_id)
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
        assignment = None
        for candidate in _candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                assignment = _canvas_client().get_assignment(
                    course_id=course_id,
                    assignment_id=candidate,
                    include_submission=False,
                )
                break
            except CanvasAPIError:
                continue
        if assignment:
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
        return None

    if resource_type == "discussion_topic" and resource_id:
        view = None
        for candidate in _candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                view = _canvas_client().get_discussion_topic_view(
                    course_id=course_id,
                    topic_id=candidate,
                )
                break
            except CanvasAPIError:
                continue
        if view:
            return {
                "course_id": course_id,
                "topic": {
                    "id": str(view.get("id", "")),
                    "title": view.get("title"),
                    "html_url": view.get("html_url"),
                },
            }
        return None

    if resource_type == "page" and resource_id_raw:
        page = _canvas_client().get_page(
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
        file_info = None
        for candidate in _candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                file_info = _canvas_client().get_file(
                    course_id=course_id,
                    file_id=candidate,
                )
                break
            except CanvasAPIError:
                continue
        if file_info:
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
        return None

    return None


def _map_discussion_entry(
    entry: dict[str, Any], include_replies: bool
) -> dict[str, Any]:
    mapped = {
        "id": str(entry.get("id", "")),
        "created_at": entry.get("created_at"),
        "updated_at": entry.get("updated_at"),
        "parent_id": str(entry["parent_id"])
        if entry.get("parent_id") is not None
        else None,
        "rating_count": entry.get("rating_count"),
        "rating_sum": entry.get("rating_sum"),
        "user_id": str(entry["user_id"]) if entry.get("user_id") is not None else None,
        "user_name": entry.get("user_name"),
        "message": entry.get("message"),
        "read_state": entry.get("read_state"),
        "forced_read_state": entry.get("forced_read_state"),
    }
    if include_replies:
        mapped["replies"] = [
            _map_discussion_entry(reply, include_replies=True)
            for reply in (entry.get("replies") or [])
            if isinstance(reply, dict)
        ]
    return mapped


def _count_discussion_entries(entries: list[dict[str, Any]]) -> int:
    total = 0
    for entry in entries:
        total += 1
        replies = entry.get("replies") or []
        if isinstance(replies, list):
            total += _count_discussion_entries(
                [reply for reply in replies if isinstance(reply, dict)]
            )
    return total


# tool handler: return today's date in iso format.
def get_today(_: dict[str, Any]) -> dict[str, Any]:
    return {"today": date.today().isoformat()}


# tool handler: list courses for the current user.
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


# tool handler: resolve a free-text query into likely courses.
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


# tool handler: list assignments in a course.
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
        include_discussion_topic=True,
        limit=limit,
    )
    items = []
    for assignment in assignments:
        assignment_id = str(assignment.get("id", ""))
        discussion_topic_id = _extract_discussion_topic_id(assignment)
        items.append(
            {
                "id": assignment_id,
                "id_aliases": _id_aliases(assignment_id, course_id=course_id),
                "name": str(assignment.get("name", "Untitled assignment")),
                "due_at": assignment.get("due_at"),
                "unlock_at": assignment.get("unlock_at"),
                "lock_at": assignment.get("lock_at"),
                "points_possible": assignment.get("points_possible"),
                "html_url": assignment.get("html_url"),
                "submission_types": assignment.get("submission_types") or [],
                "discussion_topic_id": discussion_topic_id,
                "discussion_topic_id_aliases": _id_aliases(
                    str(discussion_topic_id or ""), course_id=course_id
                ),
            }
        )
    return {"course_id": course_id, "count": len(items), "assignments": items}


# tool handler: get full details for a single assignment.
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
        include_discussion_topic=True,
    )

    assignment_id_value = str(assignment.get("id", ""))
    discussion_topic_id = _extract_discussion_topic_id(assignment)

    return {
        "course_id": course_id,
        "assignment": {
            "id": assignment_id_value,
            "id_aliases": _id_aliases(assignment_id_value, course_id=course_id),
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
            "discussion_topic_id": discussion_topic_id,
            "discussion_topic_id_aliases": _id_aliases(
                str(discussion_topic_id or ""), course_id=course_id
            ),
            "discussion_topic": assignment.get("discussion_topic")
            if isinstance(assignment.get("discussion_topic"), dict)
            else None,
            "submission": assignment.get("submission"),
        },
    }


# tool handler: list files in a course.
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


# tool handler: download a file from a course to temp storage.
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


# tool handler: list folders in a course.
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


# tool handler: list modules and optional module items in a course.
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


# tool handler: fetch a course page by slug or id.
def canvas_get_page(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    url_or_id = str(args.get("url_or_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not url_or_id:
        return {"error": "url_or_id is required"}

    if "://" in url_or_id:
        parsed = urlparse(url_or_id)
        parsed_path = unquote(parsed.path).strip("/")
        normalized_path = re.sub(r"^api/v1/", "", parsed_path)
        parts = [part for part in normalized_path.split("/") if part]
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


# tool handler: list course announcements.
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


# tool handler: list calendar events and assignments.
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


# tool handler: list users in a course.
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


# tool handler: get top-level metadata for one course.
def get_course_overview(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    course = _canvas_client().get_course(
        course_id=course_id,
        include=["term", "total_students", "teachers", "course_image"],
    )

    teachers = [
        {
            "id": str(teacher.get("id", "")),
            "display_name": teacher.get("display_name"),
            "sortable_name": teacher.get("sortable_name"),
            "avatar_image_url": teacher.get("avatar_image_url"),
            "html_url": teacher.get("html_url"),
        }
        for teacher in (course.get("teachers") or [])
        if isinstance(teacher, dict)
    ]

    return {
        "course": {
            "id": str(course.get("id", "")),
            "name": course.get("name", "Untitled course"),
            "course_code": course.get("course_code"),
            "workflow_state": course.get("workflow_state"),
            "term": course.get("term"),
            "start_at": course.get("start_at"),
            "end_at": course.get("end_at"),
            "time_zone": course.get("time_zone"),
            "default_view": course.get("default_view"),
            "public_syllabus": course.get("public_syllabus"),
            "is_favorite": course.get("is_favorite"),
            "total_students": course.get("total_students"),
            "storage_quota_mb": course.get("storage_quota_mb"),
            "grading_standard_id": course.get("grading_standard_id"),
            "apply_assignment_group_weights": course.get(
                "apply_assignment_group_weights"
            ),
            "hide_final_grades": course.get("hide_final_grades"),
            "html_url": course.get("html_url"),
            "teachers": teachers,
        }
    }


# tool handler: get syllabus metadata and optional syllabus body.
def get_course_syllabus(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_body = bool(args.get("include_body", True))
    try:
        body_char_limit = int(args.get("body_char_limit", 12000))
    except (TypeError, ValueError):
        body_char_limit = 12000
    body_char_limit = max(200, min(body_char_limit, 200000))

    course = _canvas_client().get_course(
        course_id=course_id,
        include=["syllabus_body", "term", "total_students"],
    )
    syllabus_body = course.get("syllabus_body")
    if not include_body:
        syllabus_body = None
    elif isinstance(syllabus_body, str) and len(syllabus_body) > body_char_limit:
        syllabus_body = syllabus_body[:body_char_limit]

    return {
        "course_id": str(course.get("id", "")) or course_id,
        "course_name": course.get("name", "Untitled course"),
        "course_code": course.get("course_code"),
        "term": course.get("term"),
        "syllabus_body": syllabus_body,
        "has_syllabus_body": bool(course.get("syllabus_body")),
        "syllabus_public": course.get("public_syllabus"),
        "syllabus_raw_length": len(str(course.get("syllabus_body") or "")),
        "html_url": course.get("html_url"),
    }


# tool handler: list wiki pages for a course.
def list_course_pages(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    published_only = args.get("published_only")
    if published_only is not None:
        published_only = bool(published_only)

    limit = _clamp(args.get("limit"), 100)
    pages = _canvas_client().list_pages(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        published_only=published_only,
        limit=limit,
    )
    items = [
        {
            "page_id": str(page.get("page_id", "")),
            "url": page.get("url"),
            "title": page.get("title", "Untitled page"),
            "created_at": page.get("created_at"),
            "updated_at": page.get("updated_at"),
            "published": page.get("published"),
            "front_page": page.get("front_page"),
            "hide_from_students": page.get("hide_from_students"),
            "editing_roles": page.get("editing_roles"),
            "html_url": page.get("html_url"),
        }
        for page in pages
    ]
    return {"course_id": course_id, "count": len(items), "pages": items}


# tool handler: list course navigation tabs (left sidebar entries).
def list_course_tabs(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = _clamp(args.get("limit"), 100)
    tabs = _canvas_client().list_tabs(
        course_id=course_id,
        limit=limit,
    )
    items = [_map_course_tab(tab) for tab in tabs]
    return {"course_id": course_id, "count": len(items), "tabs": items}


# tool handler: fetch one course navigation tab and optionally resolve/fetch target details.
def get_course_tab(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    tab_id = str(args.get("tab_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not tab_id:
        return {"error": "tab_id is required"}

    include_target = bool(args.get("include_target", True))
    tab = _canvas_client().get_tab(course_id=course_id, tab_id=tab_id)
    mapped_tab = _map_course_tab(tab)

    target = None
    if include_target:
        target_url = _course_tab_target_url(tab_id=tab_id, tab=mapped_tab)
        if target_url:
            target = resolve_canvas_url({"url": target_url, "fetch_details": True})

    return {
        "course_id": course_id,
        "tab_id": tab_id,
        "tab": mapped_tab,
        "target": target,
    }


# tool handler: list discussion topics for a course.
def list_discussion_topics(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    search_in = str(args.get("search_in", "title")).strip().lower()
    if search_in not in {"title", "title_or_message"}:
        return {"error": "search_in must be 'title' or 'title_or_message'"}

    limit = _clamp(args.get("limit"), 100)
    include_announcements = bool(args.get("include_announcements", False))
    only_graded = bool(args.get("only_graded", False))
    exact_title = bool(args.get("exact_title", False))
    search_value = str(args.get("search") or "").strip()
    scan_limit = 300

    api_topics = _canvas_client().list_discussion_topics(
        course_id=course_id,
        search=None,
        only_graded=False,
        exact_title=False,
        include_announcements=True,
        search_in="title",
        limit=scan_limit,
    )

    assignments = _canvas_client().list_assignments(
        course_id=course_id,
        search=None,
        include_submission=False,
        include_discussion_topic=True,
        limit=scan_limit,
    )
    assignment_topics: list[dict[str, Any]] = []
    for assignment in assignments:
        topic = _assignment_to_discussion_topic(assignment)
        if topic is not None:
            assignment_topics.append(topic)

    topic_by_id: dict[str, dict[str, Any]] = {}
    for topic in api_topics + assignment_topics:
        topic_id = str(topic.get("id", "")).strip()
        if not topic_id or topic_id in topic_by_id:
            continue
        topic_by_id[topic_id] = topic
    topics = list(topic_by_id.values())

    if not include_announcements:
        topics = [topic for topic in topics if not _is_announcement_topic(topic)]

    if only_graded:
        topics = [topic for topic in topics if topic.get("assignment_id")]

    if search_value:
        query = search_value.casefold()
        query_aliases = set(_id_aliases(search_value, course_id=course_id))

        def _matches(topic: dict[str, Any]) -> bool:
            topic_id = str(topic.get("id", ""))
            topic_aliases = set(_id_aliases(topic_id, course_id=course_id))
            assignment_value = topic.get("assignment_id")
            assignment_id = (
                str(assignment_value) if assignment_value is not None else ""
            )
            assignment_aliases = set(_id_aliases(assignment_id, course_id=course_id))
            if query_aliases and query_aliases & (topic_aliases | assignment_aliases):
                return True

            title = str(topic.get("title") or "")
            message = str(topic.get("message") or "")
            if exact_title:
                return title.casefold().strip() == query
            if search_in == "title_or_message":
                return query in title.casefold() or query in message.casefold()
            return query in title.casefold()

        topics = [topic for topic in topics if _matches(topic)]

    topics = topics[:limit]

    items = [
        {
            "id": str(topic.get("id", "")),
            "id_aliases": _id_aliases(str(topic.get("id", "")), course_id=course_id),
            "title": topic.get("title", "Untitled discussion"),
            "message": topic.get("message"),
            "posted_at": topic.get("posted_at"),
            "last_reply_at": topic.get("last_reply_at"),
            "delayed_post_at": topic.get("delayed_post_at"),
            "lock_at": topic.get("lock_at"),
            "discussion_type": topic.get("discussion_type"),
            "is_announcement": _is_announcement_topic(topic),
            "published": topic.get("published"),
            "locked": topic.get("locked"),
            "pinned": topic.get("pinned"),
            "assignment_id": str(topic["assignment_id"])
            if topic.get("assignment_id") is not None
            else None,
            "assignment_id_aliases": _id_aliases(
                str(topic["assignment_id"]), course_id=course_id
            )
            if topic.get("assignment_id") is not None
            else [],
            "points_possible": topic.get("points_possible"),
            "html_url": topic.get("html_url"),
            "source": topic.get("source", "discussion_topics_api"),
        }
        for topic in topics
    ]
    return {
        "course_id": course_id,
        "count": len(items),
        "filters": {
            "search": search_value or None,
            "search_in": search_in,
            "exact_title": exact_title,
            "only_graded": only_graded,
            "include_announcements": include_announcements,
        },
        "topics": items,
    }


# tool handler: get discussion thread entries and replies.
def get_discussion_entries(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    topic_id = str(args.get("topic_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not topic_id:
        return {"error": "topic_id is required"}

    include_replies = bool(args.get("include_replies", True))
    include_participants = bool(args.get("include_participants", True))
    limit = _clamp(args.get("limit"), 200)

    topic_candidates = _candidate_ids_for_lookup(topic_id, course_id=course_id)
    resolved_topic: dict[str, Any] | None = None
    try:
        all_topics = _canvas_client().list_discussion_topics(
            course_id=course_id,
            include_announcements=True,
            limit=300,
        )
    except CanvasAPIError as exc:
        message = str(exc)
        if _is_forbidden_message(message):
            return {
                "error": "forbidden",
                "message": message,
                "hint": "Your Canvas role/token does not allow reading this discussion.",
            }
        return {"error": message}

    for topic in all_topics:
        topic_aliases = _id_aliases(str(topic.get("id", "")), course_id=course_id)
        assignment_id = (
            str(topic["assignment_id"])
            if topic.get("assignment_id") is not None
            else ""
        )
        assignment_aliases = _id_aliases(assignment_id, course_id=course_id)
        if any(
            candidate in topic_aliases or candidate in assignment_aliases
            for candidate in topic_candidates
        ):
            resolved_topic = topic
            break

    request_ids: list[str] = []
    if resolved_topic and resolved_topic.get("id") is not None:
        request_ids.extend(
            _candidate_ids_for_lookup(str(resolved_topic["id"]), course_id=course_id)
        )
    request_ids.extend(topic_candidates)

    deduped_request_ids: list[str] = []
    for candidate in request_ids:
        if candidate and candidate not in deduped_request_ids:
            deduped_request_ids.append(candidate)

    assignment_linked_topic_id: str | None = None
    for assignment_candidate in topic_candidates:
        try:
            assignment = _canvas_client().get_assignment(
                course_id=course_id,
                assignment_id=assignment_candidate,
                include_submission=False,
                include_discussion_topic=True,
            )
        except CanvasAPIError:
            continue
        discussion_topic_id = _extract_discussion_topic_id(assignment)
        if discussion_topic_id:
            assignment_linked_topic_id = discussion_topic_id
            for candidate in _candidate_ids_for_lookup(
                discussion_topic_id, course_id=course_id
            ):
                if candidate not in deduped_request_ids:
                    deduped_request_ids.insert(0, candidate)
            if isinstance(assignment.get("discussion_topic"), dict):
                resolved_topic = assignment.get("discussion_topic")
            break

    canonical_topic: dict[str, Any] | None = None
    canonical_error: str | None = None
    for candidate in deduped_request_ids:
        try:
            canonical_topic = _canvas_client().get_discussion_topic(
                course_id=course_id,
                topic_id=candidate,
            )
            break
        except CanvasAPIError as exc:
            canonical_error = str(exc)
            continue

    if canonical_topic and canonical_topic.get("id") is not None:
        canonical_topic_id = str(canonical_topic.get("id"))
        for candidate in _candidate_ids_for_lookup(
            canonical_topic_id, course_id=course_id
        ):
            if candidate not in deduped_request_ids:
                deduped_request_ids.insert(0, candidate)

    view: dict[str, Any] | None = None
    last_error: str | None = None
    for candidate in deduped_request_ids:
        try:
            view = _canvas_client().get_discussion_topic_view(
                course_id=course_id,
                topic_id=candidate,
            )
            break
        except CanvasAPIError as exc:
            last_error = str(exc)
            continue

    if view is None:
        if last_error and _is_forbidden_message(last_error):
            return {
                "error": "forbidden",
                "message": last_error,
                "hint": "Your Canvas role/token does not allow reading this discussion.",
            }
        if last_error and _is_not_found_message(last_error) and not canonical_topic:
            return {
                "error": "not_found",
                "message": last_error,
                "topic_id": topic_id,
            }
        if canonical_topic:
            view = {"view": [], "participants": []}
        else:
            if canonical_error and _is_forbidden_message(canonical_error):
                return {
                    "error": "forbidden",
                    "message": canonical_error,
                    "hint": (
                        "Your Canvas role/token does not allow reading this discussion."
                    ),
                }
            if canonical_error and _is_not_found_message(canonical_error):
                return {
                    "error": "not_found",
                    "message": canonical_error,
                    "topic_id": topic_id,
                }
            return {
                "error": "not_found",
                "message": (
                    "Could not resolve a discussion topic from the provided id. "
                    "Try list_discussion_topics first and pass its topic id."
                ),
                "topic_id": topic_id,
            }

    topic_view_id = str(view.get("id", "")).strip()
    if not topic_view_id and isinstance(canonical_topic, dict):
        topic_view_id = str(canonical_topic.get("id") or "").strip()
    if not topic_view_id and isinstance(resolved_topic, dict):
        topic_view_id = str(resolved_topic.get("id") or "").strip()
    if not topic_view_id:
        return {
            "error": "not_found",
            "message": (
                "Canvas returned an empty discussion payload. "
                "This usually means the id does not map to a discussion topic."
            ),
            "topic_id": topic_id,
        }

    raw_entries = [
        entry for entry in (view.get("view") or []) if isinstance(entry, dict)
    ][:limit]
    entries = [_map_discussion_entry(entry, include_replies) for entry in raw_entries]

    participants = []
    if include_participants:
        participants = [
            {
                "id": str(user.get("id", "")),
                "anonymous_id": user.get("anonymous_id"),
                "display_name": user.get("display_name"),
                "avatar_image_url": user.get("avatar_image_url"),
                "html_url": user.get("html_url"),
                "pronouns": user.get("pronouns"),
            }
            for user in (view.get("participants") or [])
            if isinstance(user, dict)
        ]

    title = str(view.get("title") or "").strip()
    if not title and isinstance(canonical_topic, dict):
        title = str(canonical_topic.get("title") or "").strip()
    if not title and isinstance(resolved_topic, dict):
        title = str(resolved_topic.get("title") or "").strip()

    if (
        not title
        and not str(view.get("message") or "").strip()
        and not str((canonical_topic or {}).get("message") or "").strip()
        and not entries
        and resolved_topic is None
        and canonical_topic is None
    ):
        return {
            "error": "not_found",
            "message": (
                "Canvas did not return a valid discussion payload for this id. "
                "Pass a discussion topic id from list_discussion_topics."
            ),
            "topic_id": topic_id,
        }

    topic_message = _first_non_none(
        view.get("message"),
        canonical_topic.get("message") if isinstance(canonical_topic, dict) else None,
        resolved_topic.get("message") if isinstance(resolved_topic, dict) else None,
    )
    topic_assignment_id = _first_non_none(
        str(view["assignment_id"]) if view.get("assignment_id") is not None else None,
        str(canonical_topic["assignment_id"])
        if isinstance(canonical_topic, dict)
        and canonical_topic.get("assignment_id") is not None
        else None,
        str(resolved_topic["assignment_id"])
        if isinstance(resolved_topic, dict)
        and resolved_topic.get("assignment_id") is not None
        else None,
    )
    topic_discussion_type = _first_non_none(
        view.get("discussion_type"),
        canonical_topic.get("discussion_type")
        if isinstance(canonical_topic, dict)
        else None,
        resolved_topic.get("discussion_type")
        if isinstance(resolved_topic, dict)
        else None,
    )
    topic_html_url = _first_non_none(
        view.get("html_url"),
        canonical_topic.get("html_url") if isinstance(canonical_topic, dict) else None,
        resolved_topic.get("html_url") if isinstance(resolved_topic, dict) else None,
    )

    return {
        "course_id": course_id,
        "requested_topic_id": topic_id,
        "requested_topic_id_aliases": topic_candidates,
        "assignment_linked_topic_id": assignment_linked_topic_id,
        "resolved_topic_id": topic_view_id,
        "resolved_topic_id_aliases": _id_aliases(topic_view_id, course_id=course_id),
        "topic": {
            "id": topic_view_id,
            "title": title or "Untitled discussion",
            "message": topic_message,
            "assignment_id": topic_assignment_id,
            "discussion_type": topic_discussion_type,
            "published": view.get("published"),
            "locked": view.get("locked"),
            "html_url": topic_html_url,
        },
        "participants_count": len(participants),
        "participants": participants,
        "top_level_entries_count": len(entries),
        "total_entries_count": _count_discussion_entries(entries),
        "entries": entries,
    }


# tool handler: list assignment groups and optional assignment details.
def list_assignment_groups(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_assignments = bool(args.get("include_assignments", False))
    include_submission = bool(args.get("include_submission", False))
    limit = _clamp(args.get("limit"), 100)
    groups = _canvas_client().list_assignment_groups(
        course_id=course_id,
        include_assignments=include_assignments,
        include_submission=include_submission,
        limit=limit,
    )

    items = []
    for group in groups:
        assignments = []
        if include_assignments:
            for assignment in group.get("assignments") or []:
                if not isinstance(assignment, dict):
                    continue
                assignment_id = str(assignment.get("id", ""))
                discussion_topic_id = _extract_discussion_topic_id(assignment)
                assignments.append(
                    {
                        "id": assignment_id,
                        "id_aliases": _id_aliases(assignment_id, course_id=course_id),
                        "name": assignment.get("name", "Untitled assignment"),
                        "due_at": assignment.get("due_at"),
                        "unlock_at": assignment.get("unlock_at"),
                        "lock_at": assignment.get("lock_at"),
                        "points_possible": assignment.get("points_possible"),
                        "submission_types": assignment.get("submission_types") or [],
                        "html_url": assignment.get("html_url"),
                        "discussion_topic_id": discussion_topic_id,
                        "discussion_topic_id_aliases": _id_aliases(
                            str(discussion_topic_id or ""), course_id=course_id
                        ),
                        "submission": assignment.get("submission")
                        if include_submission
                        else None,
                    }
                )

        items.append(
            {
                "id": str(group.get("id", "")),
                "name": group.get("name", "Untitled assignment group"),
                "group_weight": group.get("group_weight"),
                "position": group.get("position"),
                "rules": group.get("rules"),
                "assignments_count": group.get("assignments_count"),
                "assignments": assignments,
            }
        )

    return {"course_id": course_id, "count": len(items), "assignment_groups": items}


# tool handler: list submissions for a course and student.
def list_course_submissions(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_raw = args.get("include")
    include: list[str] | None = None
    if include_raw is not None:
        if not isinstance(include_raw, list):
            return {"error": "include must be an array of strings"}
        include = [str(item).strip() for item in include_raw if str(item).strip()]

    assignment_ids_raw = args.get("assignment_ids")
    assignment_ids: list[str] | None = None
    if assignment_ids_raw is not None:
        if not isinstance(assignment_ids_raw, list):
            return {"error": "assignment_ids must be an array of strings"}
        assignment_ids = []
        for item in assignment_ids_raw:
            canonical_id = _expand_canvas_id(str(item), course_id=course_id)
            if canonical_id and canonical_id not in assignment_ids:
                assignment_ids.append(canonical_id)

    student_id = str(args.get("student_id", "self")).strip() or "self"

    limit = _clamp(args.get("limit"), 200)
    try:
        submissions = _canvas_client().list_submissions(
            course_id=course_id,
            student_id=student_id,
            assignment_ids=assignment_ids,
            include=include,
            grouped=bool(args.get("grouped", False)),
            workflow_state=str(args.get("workflow_state"))
            if args.get("workflow_state")
            else None,
            submitted_since=str(args.get("submitted_since"))
            if args.get("submitted_since")
            else None,
            graded_since=str(args.get("graded_since"))
            if args.get("graded_since")
            else None,
            limit=limit,
        )
    except CanvasAPIError as exc:
        message = str(exc)
        if _is_forbidden_message(message):
            return {
                "error": "forbidden",
                "message": message,
                "hint": (
                    "To read submissions for non-self users, your Canvas token must "
                    "have submission read access and your role must permit viewing "
                    "other students in this course."
                ),
                "requested_student_id": student_id,
            }
        return {"error": message}

    flattened_submissions: list[dict[str, Any]] = []
    grouped_shell_count = 0
    for submission in submissions:
        grouped_rows = submission.get("submissions")
        if (
            isinstance(grouped_rows, list)
            and submission.get("assignment_id") is None
            and submission.get("grade") is None
        ):
            if grouped_rows:
                for grouped in grouped_rows:
                    if not isinstance(grouped, dict):
                        continue
                    merged = dict(grouped)
                    if merged.get("user_id") is None:
                        merged["user_id"] = submission.get("user_id")
                    if merged.get("course_id") is None:
                        merged["course_id"] = submission.get("course_id")
                    if merged.get("section_id") is None:
                        merged["section_id"] = submission.get("section_id")
                    flattened_submissions.append(merged)
            else:
                grouped_shell_count += 1
        else:
            flattened_submissions.append(submission)

    submissions = flattened_submissions
    if not submissions and grouped_shell_count > 0:
        return {
            "error": "access_limited",
            "message": (
                "Canvas returned grouped submission shells without assignment data. "
                "This integration token/role likely lacks course-wide submissions feed access."
            ),
            "hint": (
                "Use get_assignment_details(include_submission=true) for specific "
                "assignments, or update Canvas token scopes/role permissions."
            ),
            "requested_student_id": student_id,
        }

    items = []
    for submission in submissions:
        assignment = submission.get("assignment")
        items.append(
            {
                "id": str(submission.get("id", "")),
                "assignment_id": str(submission["assignment_id"])
                if submission.get("assignment_id") is not None
                else None,
                "assignment_id_aliases": _id_aliases(
                    str(submission["assignment_id"]), course_id=course_id
                )
                if submission.get("assignment_id") is not None
                else [],
                "assignment_name": assignment.get("name")
                if isinstance(assignment, dict)
                else None,
                "user_id": str(submission["user_id"])
                if submission.get("user_id") is not None
                else None,
                "score": submission.get("score"),
                "grade": submission.get("grade"),
                "entered_score": submission.get("entered_score"),
                "entered_grade": submission.get("entered_grade"),
                "submitted_at": submission.get("submitted_at"),
                "graded_at": submission.get("graded_at"),
                "late": submission.get("late"),
                "missing": submission.get("missing"),
                "excused": submission.get("excused"),
                "workflow_state": submission.get("workflow_state"),
                "submission_type": submission.get("submission_type"),
                "attempt": submission.get("attempt"),
                "seconds_late": submission.get("seconds_late"),
                "assignment": assignment if isinstance(assignment, dict) else None,
                "url": submission.get("url"),
                "body": submission.get("body"),
                "preview_url": submission.get("preview_url"),
                "attachments": submission.get("attachments") or [],
                "submission_comments": submission.get("submission_comments") or [],
                "submission_history": submission.get("submission_history") or [],
                "rubric_assessment": submission.get("rubric_assessment"),
                "media_comment": submission.get("media_comment"),
                "group": submission.get("group"),
                "user": submission.get("user"),
                "discussion_entries": submission.get("discussion_entries") or [],
                "content": submission.get("body") or submission.get("url"),
                "raw_submission": submission,
            }
        )

    response: dict[str, Any] = {
        "course_id": course_id,
        "count": len(items),
        "submissions": items,
    }
    if not items and student_id not in {"self", "me", "current"}:
        response["warning"] = (
            "No submissions were returned for a non-self query. This may be due to "
            "Canvas token scope or role permissions."
        )
        response["hint"] = (
            "Grant submission read access for all students in the course or query "
            "student_id='self'."
        )
    return response


# tool handler: summarize course grades from enrollments and submissions.
def get_course_grade_summary(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    student_id = str(args.get("student_id", "self")).strip() or "self"

    course = _canvas_client().get_course(course_id=course_id, include=["term"])
    enrollments = _canvas_client().list_enrollments(
        course_id=course_id,
        user_id=student_id,
        include=["grades"],
        limit=10,
    )
    enrollment = enrollments[0] if enrollments else {}

    submissions = _canvas_client().list_submissions(
        course_id=course_id,
        student_id=student_id,
        include=["assignment"],
        grouped=False,
        limit=300,
    )

    missing_count = 0
    late_count = 0
    excused_count = 0
    earned_points = 0.0
    possible_points = 0.0

    for submission in submissions:
        if submission.get("missing"):
            missing_count += 1
        if submission.get("late"):
            late_count += 1
        if submission.get("excused"):
            excused_count += 1

        assignment = submission.get("assignment")
        if not isinstance(assignment, dict):
            continue
        points_possible = assignment.get("points_possible")
        if points_possible is None:
            continue
        try:
            points_possible_val = float(points_possible)
        except (TypeError, ValueError):
            continue
        if points_possible_val <= 0:
            continue
        possible_points += points_possible_val
        score = submission.get("score")
        try:
            earned_points += float(score) if score is not None else 0.0
        except (TypeError, ValueError):
            earned_points += 0.0

    raw_percent = None
    if possible_points > 0:
        raw_percent = (earned_points / possible_points) * 100.0

    assignment_groups = _canvas_client().list_assignment_groups(
        course_id=course_id,
        include_assignments=True,
        include_submission=True,
        limit=100,
    )
    group_breakdown = []
    for group in assignment_groups:
        assignments = [
            assignment
            for assignment in (group.get("assignments") or [])
            if isinstance(assignment, dict)
        ]
        group_possible = 0.0
        group_earned = 0.0
        for assignment in assignments:
            points_possible = assignment.get("points_possible")
            if points_possible is None:
                continue
            try:
                points_possible_val = float(points_possible)
            except (TypeError, ValueError):
                continue
            if points_possible_val <= 0:
                continue
            submission = assignment.get("submission")
            if isinstance(submission, dict) and submission.get("excused"):
                continue
            group_possible += points_possible_val
            score = None
            if isinstance(submission, dict):
                score = submission.get("score")
            try:
                group_earned += float(score) if score is not None else 0.0
            except (TypeError, ValueError):
                group_earned += 0.0

        group_percent = None
        if group_possible > 0:
            group_percent = (group_earned / group_possible) * 100.0

        weight = group.get("group_weight")
        weighted_contribution = None
        try:
            if group_percent is not None and weight is not None:
                weighted_contribution = (float(weight) / 100.0) * group_percent
        except (TypeError, ValueError):
            weighted_contribution = None

        group_breakdown.append(
            {
                "id": str(group.get("id", "")),
                "name": group.get("name", "Untitled assignment group"),
                "group_weight": weight,
                "earned_points": round(group_earned, 4),
                "possible_points": round(group_possible, 4),
                "percent": round(group_percent, 4)
                if group_percent is not None
                else None,
                "weighted_contribution_estimate": round(weighted_contribution, 4)
                if weighted_contribution is not None
                else None,
            }
        )

    return {
        "course_id": str(course.get("id", "")) or course_id,
        "course_name": course.get("name", "Untitled course"),
        "term": course.get("term"),
        "student_id": student_id,
        "enrollment_type": enrollment.get("type"),
        "enrollment_state": enrollment.get("enrollment_state"),
        "grades": enrollment.get("grades") if isinstance(enrollment, dict) else None,
        "raw_points": {
            "earned": round(earned_points, 4),
            "possible": round(possible_points, 4),
            "percent": round(raw_percent, 4) if raw_percent is not None else None,
        },
        "submission_counts": {
            "total": len(submissions),
            "missing": missing_count,
            "late": late_count,
            "excused": excused_count,
        },
        "assignment_group_breakdown": group_breakdown,
    }


# tool handler: parse a canvas url and optionally fetch object details.
def resolve_canvas_url(args: dict[str, Any]) -> dict[str, Any]:
    url = str(args.get("url", "")).strip()
    if not url:
        return {"error": "url is required"}

    parsed = urlparse(url)
    path = unquote(parsed.path).strip("/")
    path = re.sub(r"^api/v1/", "", path)
    parts = [part for part in path.split("/") if part]

    course_id_raw, resource_type, resource_id_raw = _parse_canvas_course_resource(parts)

    course_id = str(course_id_raw).strip() if course_id_raw else None
    resource_id = (
        _expand_canvas_id(resource_id_raw, course_id=course_id)
        if resource_id_raw
        else None
    )
    recommended_tool = _recommended_tool_for_resource(resource_type)

    fetch_details = bool(args.get("fetch_details", True))
    details: dict[str, Any] | None = None
    detail_error: str | None = None

    if fetch_details and course_id and resource_type:
        try:
            details = _resolve_canvas_resource_details(
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
        "course_id_aliases": _id_aliases(course_id_raw or "", course_id=course_id),
        "resource_type": resource_type,
        "resource_id_raw": resource_id_raw,
        "resource_id": resource_id,
        "resource_id_aliases": _id_aliases(resource_id_raw or "", course_id=course_id),
        "recommended_tool": recommended_tool,
        "details": details,
        "detail_error": detail_error,
    }


# tool handler: aggregate a compact course context snapshot.
def get_course_context_snapshot(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_syllabus_body = bool(args.get("include_syllabus_body", False))
    upcoming_limit = _clamp(args.get("upcoming_limit"), 20)
    announcements_limit = _clamp(args.get("announcements_limit"), 10)
    modules_limit = _clamp(args.get("modules_limit"), 20)
    module_items_limit = _clamp(args.get("module_items_limit"), 50)

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
