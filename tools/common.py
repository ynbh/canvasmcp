from __future__ import annotations

from functools import lru_cache
import getpass
from pathlib import Path
import re
import tempfile
from typing import Any
from urllib.parse import unquote, urlparse

from canvas_api import CanvasAPIError, create_canvas_client_from_env

MAX_TOOL_LIMIT = 300


def normalize(text: str | None) -> str:
    if not text:
        return ""
    cleaned = "".join(
        ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text
    )
    return " ".join(cleaned.split())


def clamp(value: int | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(parsed, MAX_TOOL_LIMIT))


def download_dir() -> Path:
    username = re.sub(r"[^A-Za-z0-9._-]+", "_", getpass.getuser()).strip("._")
    if not username:
        username = "user"
    return Path(tempfile.gettempdir()) / f"canvas_files_{username}"


def safe_filename(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    if not sanitized:
        return "canvas_file"
    return sanitized[:180]


def download_file_path(
    root: Path, course_id: str, file_id: str, filename: str
) -> Path:
    return root / f"course-{course_id}_file-{file_id}_{safe_filename(filename)}"


@lru_cache(maxsize=1)
def canvas_client():
    return create_canvas_client_from_env()


def course_id_prefix(course_id: str | None) -> str | None:
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


def expand_canvas_id(raw_id: str, *, course_id: str | None = None) -> str:
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

    prefix = course_id_prefix(course_id)
    if prefix:
        return f"{prefix}000000{trimmed}"

    return trimmed


def collapse_canvas_id(raw_id: str) -> str:
    match = re.fullmatch(r"(\d+)000000(\d+)", raw_id.strip())
    if not match:
        return raw_id
    return f"{match.group(1)}~{match.group(2)}"


def short_canvas_id(raw_id: str) -> str:
    match = re.fullmatch(r"(\d+)000000(\d+)", raw_id.strip())
    if match:
        return match.group(2)
    tilde_match = re.fullmatch(r"(\d+)~(\d+)", raw_id.strip())
    if tilde_match:
        return tilde_match.group(2)
    return raw_id.strip()


def id_aliases(raw_id: str, *, course_id: str | None = None) -> list[str]:
    trimmed = str(raw_id).strip()
    if not trimmed:
        return []

    candidates: list[str] = []
    expanded = expand_canvas_id(trimmed, course_id=course_id)
    for value in (
        trimmed,
        expanded,
        collapse_canvas_id(expanded),
        short_canvas_id(expanded),
    ):
        if value and value not in candidates:
            candidates.append(value)
    return candidates


def candidate_ids_for_lookup(
    raw_id: str, *, course_id: str | None = None
) -> list[str]:
    aliases = id_aliases(raw_id, course_id=course_id)
    if not aliases:
        return []

    expanded = expand_canvas_id(raw_id, course_id=course_id)
    ordered: list[str] = []
    for value in [expanded, *aliases]:
        if value and value not in ordered:
            ordered.append(value)
    return ordered


def extract_discussion_topic_id(item: dict[str, Any]) -> str | None:
    direct = item.get("discussion_topic_id")
    if direct is not None:
        return str(direct)
    topic = item.get("discussion_topic")
    if isinstance(topic, dict) and topic.get("id") is not None:
        return str(topic["id"])
    return None


def is_announcement_topic(topic: dict[str, Any]) -> bool:
    return bool(
        topic.get("announcement")
        or topic.get("is_announcement")
        or str(topic.get("discussion_type", "")).casefold() == "announcement"
    )


def assignment_to_discussion_topic(assignment: dict[str, Any]) -> dict[str, Any] | None:
    discussion_topic_id = extract_discussion_topic_id(assignment)
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

    html_url = discussion_topic.get("html_url") or assignment.get("html_url")

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


def is_forbidden_message(message: str) -> bool:
    lowered = message.casefold()
    return (
        "forbidden" in lowered
        or "not authorised" in lowered
        or "not authorized" in lowered
        or "unauthorized" in lowered
    )


def is_not_found_message(message: str) -> bool:
    lowered = message.casefold()
    return "not found" in lowered or "could not find" in lowered


def first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def first_non_empty_str(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def course_tab_target_url(tab_id: str, tab: dict[str, Any]) -> str:
    target_url = first_non_empty_str(
        tab.get("html_url"),
        tab.get("full_url"),
        tab.get("url"),
    )
    if tab_id.strip().lower() == "home" and re.fullmatch(
        r"(?:https?://[^/]+)?/courses/\d+", target_url.rstrip("/")
    ):
        return f"{target_url.rstrip('/')}/home"
    return target_url


def parse_canvas_course_resource(
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


def recommended_tool_for_resource(resource_type: str | None) -> str | None:
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


def map_discussion_entry(
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
            map_discussion_entry(reply, include_replies=True)
            for reply in (entry.get("replies") or [])
            if isinstance(reply, dict)
        ]
    return mapped


def count_discussion_entries(entries: list[dict[str, Any]]) -> int:
    total = 0
    for entry in entries:
        total += 1
        replies = entry.get("replies") or []
        if isinstance(replies, list):
            total += count_discussion_entries(
                [reply for reply in replies if isinstance(reply, dict)]
            )
    return total


def parse_canvas_url_path(url: str) -> tuple[Any, str, list[str]]:
    parsed = urlparse(url)
    path = unquote(parsed.path).strip("/")
    path = re.sub(r"^api/v1/", "", path)
    parts = [part for part in path.split("/") if part]
    return parsed, path, parts
