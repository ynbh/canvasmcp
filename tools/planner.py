from __future__ import annotations

from datetime import date, datetime
from typing import Any

from tools.common import canvas_client, invalid_argument, looks_like_canvas_id, truncate_html

# Kinds of To Do item Canvas lets you mark done or dismiss (its "plannable" types).
PLANNABLE_TYPES = (
    "assignment",
    "quiz",
    "discussion_topic",
    "wiki_page",
    "planner_note",
    "calendar_event",
    "assessment_request",
)
TITLE_LIMIT = 255
DETAILS_LIMIT = 10000
NOTE_FIELDS = ("title", "details", "todo_date", "course_id")


def _flag(value: bool) -> str:
    return "true" if value else "false"  # Canvas reads these strings; Python's "False" isn't one it knows


def _valid_date(value: Any) -> str:
    """A date (YYYY-MM-DD) or ISO date-time, as given; raises ValueError otherwise."""
    text = str(value).strip()
    try:
        if len(text) == 10:
            date.fromisoformat(text)
        else:
            datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"not a date: {text!r}") from None
    return text


def _bad_id(name: str, value: str) -> dict[str, Any] | None:
    # IDs go into the paths of write requests, so anything but a Canvas ID is refused before a request is made.
    return None if looks_like_canvas_id(value) else invalid_argument(f"{name} must be a Canvas ID")


def _map_note(note: dict[str, Any]) -> dict[str, Any]:
    return {
        "note_id": str(note.get("id", "")),
        "title": note.get("title"),
        "details": truncate_html(note.get("description") or note.get("details"), limit=DETAILS_LIMIT),
        "todo_date": note.get("todo_date"),
        "course_id": str(note["course_id"]) if note.get("course_id") else None,
        "state": note.get("workflow_state"),
    }


def _map_item(item: dict[str, Any]) -> dict[str, Any]:
    plannable = item.get("plannable") or {}
    override = item.get("planner_override") or {}
    submissions = item.get("submissions") if isinstance(item.get("submissions"), dict) else {}
    is_note = item.get("plannable_type") == "planner_note"
    return {
        "plannable_type": item.get("plannable_type"),
        "plannable_id": str(item.get("plannable_id", "")),
        "title": plannable.get("title") or plannable.get("name"),
        "date": item.get("plannable_date"),
        "course_id": str(item["course_id"]) if item.get("course_id") else None,
        "context_name": item.get("context_name"),
        "done": bool(override.get("marked_complete")),
        "dismissed": bool(override.get("dismissed")),
        "submitted": submissions.get("submitted") if submissions else None,
        "graded": submissions.get("graded") if submissions else None,
        "details": truncate_html(plannable.get("details"), limit=2000) if is_note else None,
        "html_url": item.get("html_url"),
    }


def list_planner_items(args: dict[str, Any]) -> dict[str, Any]:
    try:
        start = _valid_date(args["start_date"]) if args.get("start_date") else None
        end = _valid_date(args["end_date"]) if args.get("end_date") else None
    except ValueError as exc:
        return invalid_argument(f"start_date and end_date must be dates (YYYY-MM-DD): {exc}")
    items = canvas_client().list_planner_items(
        start_date=start,
        end_date=end,
        incomplete_only=bool(args.get("incomplete_only", False)),
        limit=int(args.get("limit", 100)),
    )
    mapped = [_map_item(item) for item in items]
    return {"start_date": start, "end_date": end, "count": len(mapped), "items": mapped}


def _note_fields(args: dict[str, Any]) -> dict[str, Any]:
    """Canvas planner-note fields from the arguments given, or an error result for the first bad one."""
    fields: dict[str, Any] = {}
    if "title" in args:
        title = str(args["title"]).strip()
        if not title:
            return invalid_argument("title can't be blank")
        if len(title) > TITLE_LIMIT:
            return invalid_argument(f"title must be at most {TITLE_LIMIT} characters")
        fields["title"] = title
    if "details" in args:
        if len(args["details"]) > DETAILS_LIMIT:
            return invalid_argument(f"details must be at most {DETAILS_LIMIT} characters")
        fields["details"] = args["details"]
    if "todo_date" in args:
        try:
            fields["todo_date"] = _valid_date(args["todo_date"])
        except ValueError as exc:
            return invalid_argument(f"todo_date must be a date (YYYY-MM-DD) or ISO date-time: {exc}")
    if "course_id" in args:
        course_id = str(args["course_id"]).strip()
        if error := _bad_id("course_id", course_id):
            return error
        fields["course_id"] = course_id
    return fields


def create_todo_note(args: dict[str, Any]) -> dict[str, Any]:
    fields = _note_fields(args)
    if "error" in fields:
        return fields
    note = canvas_client().create_planner_note(fields=fields)
    return {"created": True, "note": _map_note(note)}


def update_todo_note(args: dict[str, Any]) -> dict[str, Any]:
    note_id = str(args.get("note_id", "")).strip()
    if error := _bad_id("note_id", note_id):
        return error
    fields = _note_fields(args)
    if "error" in fields:
        return fields
    if not fields:
        return invalid_argument(f"give at least one of {', '.join(NOTE_FIELDS)} to change")
    note = canvas_client().update_planner_note(note_id=note_id, fields=fields)
    return {"updated": True, "note": _map_note(note)}


def delete_todo_note(args: dict[str, Any]) -> dict[str, Any]:
    note_id = str(args.get("note_id", "")).strip()
    if error := _bad_id("note_id", note_id):
        return error
    client = canvas_client()
    note = client.get_planner_note(note_id=note_id)  # confirms it's your own note before deleting it
    client.delete_planner_note(note_id=note_id)
    return {"deleted": True, "note": _map_note(note)}


def set_todo_item_state(args: dict[str, Any]) -> dict[str, Any]:
    plannable_type = str(args.get("plannable_type", "")).strip()
    plannable_id = str(args.get("plannable_id", "")).strip()
    if error := _bad_id("plannable_id", plannable_id):
        return error
    state = {
        field: _flag(args[name])
        for name, field in (("done", "marked_complete"), ("dismissed", "dismissed"))
        if name in args
    }
    if not state:
        return invalid_argument("give done, dismissed, or both")

    client = canvas_client()
    existing = next(
        (
            override
            for override in client.list_planner_overrides()
            if override.get("plannable_type") == plannable_type
            and str(override.get("plannable_id")) == plannable_id
        ),
        None,
    )
    if existing:
        override = client.update_planner_override(override_id=str(existing["id"]), state=state)
    else:
        override = client.create_planner_override(
            plannable_type=plannable_type, plannable_id=plannable_id, state=state
        )
    return {
        "plannable_type": plannable_type,
        "plannable_id": plannable_id,
        "done": bool(override.get("marked_complete")),
        "dismissed": bool(override.get("dismissed")),
        "note": "Only changes your To Do list; nothing is submitted.",
    }
