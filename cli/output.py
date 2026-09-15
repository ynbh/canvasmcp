from __future__ import annotations

import json
import re
import shlex
import sys
import textwrap
from datetime import datetime
from enum import Enum
from html.parser import HTMLParser
from typing import Any

import click
import typer
from rich.console import Console


class OutputMode(str, Enum):
    auto = "auto"
    pretty = "pretty"
    json = "json"


# Lists and details share field ordering; unknown fields remain visible.
FIELD_ORDER = {
    "courses": "id name course_code term_name state",
    "matches": "id name course_code score term_name state",
    "assignments": "id name due_at points_possible submission",
    "assignment": "id name due_at lock_at points_possible submission description rubric",
    "jobs": "id status assignment_name course_id assignment_id submit_at filenames error",
    "files": "id display_name filename local_path path size error",
    "folders": "id full_name name files_count folders_count",
    "pages": "page_id title url published updated_at",
    "people": "id name display_name email enrollments",
    "tabs": "id label hidden visibility url",
    "topics": "id title posted_at discussion_type message",
    "announcements": "id title course_id posted_at message",
    "items": "id title type due_at html_url",
    "todo": "type course_id assignment_id title due_at points",
    "entries": "id user_id created_at message replies",
    "submissions": "id assignment_id assignment_name workflow_state attempt score grade submitted_at missing late excused",
    "modules": "id name state unlock_at items_count items",
    "assignment_groups": "id name group_weight rules assignments",
    "profiles": "name selected active auth_status resolved_canvas_base_url detected_canvas_domains",
    "course": "id name course_code workflow_state term time_zone teachers",
    "page": "page_id title url updated_at body",
    "auth": "auth_verified auth_status error selected_chrome_profile resolved_canvas_base_url auth_mode",
}
SECONDARY = {
    "id_aliases",
    "assignment_id_aliases",
    "discussion_topic_id_aliases",
    "avatar_image_url",
    "items_url",
    "plist_label",
    "caffeinate_pid",
    "cookie_file",
    "probe_url",
    "probe_content_type",
    "probe_location",
    "selected_chrome_profile_path",
    "resolved_chrome_profile_path",
}
PRIORITY = (
    "error",
    "message",
    "refuse_reasons",
    "warning",
    "warnings",
    "hint",
    "errors",
    "grade_estimate_disclaimer",
)
HTML_FIELDS = {
    "body",
    "description",
    "message",
    "syllabus_body",
    "content",
    "long_description",
}
EXACT_FIELDS = {
    "path",
    "local_path",
    "preview_token",
    "filename",
    "filenames",
    "url",
    "html_url",
}


class _HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        if self.hidden:
            return
        if tag in {"p", "div", "br", "li", "pre", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")
        if tag == "a":
            self.links.append(dict(attrs).get("href") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
            return
        if self.hidden:
            return
        if tag == "a" and self.links:
            href = self.links.pop()
            if href:
                self.parts.append(f" ({href})")
        if tag in {"p", "div", "li", "pre", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def _literal(value: Any) -> str:
    return re.sub(
        r"[\x00-\x08\x0b-\x1f\x7f-\x9f]", lambda m: f"\\x{ord(m[0]):02x}", str(value)
    )


def _label(key: str) -> str:
    return key.replace("_", " ").capitalize()


def _value(value: Any, key: str = "") -> str:
    if value is None:
        return "not supplied"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, str) and key.endswith("_at"):
        try:
            stamp = datetime.fromisoformat(value)
        except ValueError:
            pass
        else:
            if stamp.tzinfo is not None:
                return stamp.isoformat(sep=" ")
    if (
        isinstance(value, str)
        and key in HTML_FIELDS
        and re.search(r"</?[a-zA-Z][^>]*>", value)
    ):
        parser = _HTMLText()
        parser.feed(value)
        return "".join(parser.parts).strip()
    return str(value)


def output_mode() -> OutputMode:
    context = click.get_current_context(silent=True)
    mode = context.meta.get("output", OutputMode.auto) if context else OutputMode.auto
    if mode != OutputMode.auto:
        return OutputMode(mode)
    machine_output = context.meta.get("machine_output", False) if context else False
    return (
        OutputMode.json
        if machine_output or not sys.stdout.isatty()
        else OutputMode.pretty
    )


class _Pretty:
    def __init__(self, console: Console) -> None:
        self.console = console
        self.omitted = False

    def line(self, text: str = "", *, indent: int = 0, exact: bool = False) -> None:
        prefix = " " * indent
        for line in _literal(text).splitlines() or [""]:
            lines = (
                [line]
                if exact
                else textwrap.wrap(
                    line,
                    width=max(20, self.console.width - indent),
                    break_long_words=False,
                    break_on_hyphens=False,
                    replace_whitespace=False,
                )
                or [""]
            )
            for part in lines:
                self.console.print(
                    prefix + part, markup=False, highlight=False, soft_wrap=True
                )

    def field(self, label: str, value: Any, *, key: str = "", indent: int = 0) -> None:
        exact = key in EXACT_FIELDS or key.endswith(("_id", "_path")) or key == "id"
        self.line(f"{label}: {_value(value, key)}", indent=indent, exact=exact)

    def record(
        self, data: Any, *, kind: str = "", indent: int = 0, full: bool = False
    ) -> None:
        if not isinstance(data, dict):
            self.line(_value(data, kind), indent=indent, exact=kind in EXACT_FIELDS)
            return
        ordered = (*PRIORITY, *FIELD_ORDER.get(kind, "").split(), *data)
        for key in dict.fromkeys(ordered):
            if key not in data:
                continue
            value = data[key]
            if not full and key in SECONDARY:
                self.omitted = True
                continue
            if isinstance(value, dict):
                self.line(f"{_label(key)}:", indent=indent)
                if value:
                    self.record(
                        value, kind=key, indent=indent + 2, full=full or key in PRIORITY
                    )
                else:
                    self.line("No fields returned", indent=indent + 2)
            elif isinstance(value, list):
                self.collection(key, value, indent=indent, full=full or key in PRIORITY)
            else:
                self.field(_label(key), value, key=key, indent=indent)

    def collection(
        self, key: str, rows: list[Any], *, indent: int = 0, full: bool = False
    ) -> None:
        self.line(f"{_label(key)} ({len(rows)} returned)", indent=indent)
        if not rows:
            self.line("None returned", indent=indent + 2)
        for index, row in enumerate(rows):
            if index and isinstance(row, dict):
                self.line()
            if isinstance(row, dict) and key in FIELD_ORDER and not full:
                title_key = next(
                    (
                        name
                        for name in (
                            "name",
                            "title",
                            "display_name",
                            "assignment_name",
                            "filename",
                            "label",
                        )
                        if row.get(name)
                    ),
                    None,
                )
                if title_key:
                    heading = str(row[title_key])
                    if row.get("id") is not None:
                        self.field("ID", row["id"], key="id", indent=indent + 2)
                    self.line(heading, indent=indent + 2)
                    row = {
                        name: value
                        for name, value in row.items()
                        if name not in {title_key, "id"}
                    }
            self.record(row, kind=key, indent=indent + 2, full=full)

    def job(self, job: dict[str, Any]) -> None:
        primary = (
            "id",
            "status",
            "assignment_name",
            "course_id",
            "assignment_id",
            "submit_at",
            "filenames",
            "file_ids",
            "body",
            "caffeinate",
            "fired_at",
            "error",
        )
        for key in primary:
            value = job.get(key)
            if value is None or value == []:
                continue
            if key == "caffeinate":
                self.field("Keep-awake requested", value)
            elif key == "body":
                self.field("Text preview (first 240 characters)", str(value)[:240])
                self.omitted = True
            elif isinstance(value, list):
                self.collection(key, value)
            else:
                self.field(_label(key), value, key=key)
        secondary = {
            "created_at",
            "submission_type",
            "result",
            "plist_label",
            "caffeinate_pid",
        }
        extras = {
            key: value
            for key, value in job.items()
            if key not in {*primary, *secondary}
        }
        self.record(extras, full=True)
        if job.get("result") is not None:
            self.line("Submission result:")
            self.record(job["result"], indent=2)
        self.omitted |= bool(secondary.intersection(job))


def _preview(view: _Pretty, result: dict[str, Any]) -> None:
    refused = result.get("ok") is False
    mode = (
        "submit immediately on confirmation"
        if result.get("now")
        else "scheduled submission"
    )
    view.line("PREVIEW REFUSED" if refused else f"PREVIEW — {mode} — nothing submitted")
    keys = (
        "assignment_name",
        "course_id",
        "assignment_id",
        "submit_at",
        "due_at",
        "lock_at",
        "unlock_at",
        "planned_payload",
        "current_attempt",
        "requires_override",
        "warnings",
        "refuse_reasons",
        "message",
        "expires_at",
        "preview_token",
    )
    view.record({key: result[key] for key in keys if key in result})
    if result.get("pending_job"):
        view.line("Existing pending job:")
        view.job(result["pending_job"])
    if not refused and result.get("preview_token"):
        view.line("Confirm:")
        view.line(
            f"canvas assignments submissions confirm {shlex.quote(str(result['preview_token']))}",
            exact=True,
        )
    secondary = {
        "ok",
        "now",
        "auth_status",
        "submission_types",
        "allowed_extensions",
        "allowed_attempts",
        "pending_job",
    }
    view.record(
        {key: value for key, value in result.items() if key not in {*keys, *secondary}},
        full=True,
    )
    view.omitted |= bool(secondary.intersection(result))


def _submission(view: _Pretty, result: dict[str, Any], tool_name: str) -> None:
    cleanup = result.get("file_cleanup") or []
    cleanup_failed = any(
        isinstance(item, dict) and item.get("error") for item in cleanup
    )
    if tool_name == "cancel_scheduled_submission":
        view.line(
            "CANCELLED — file cleanup incomplete" if cleanup_failed else "CANCELLED"
        )
    elif result.get("now"):
        view.line("SUBMITTED")
    else:
        view.line("SCHEDULED — pending (not submitted)")
    excluded = {"ok", "now", "file_cleanup"}
    if "job" in result:
        view.job(result["job"])
        excluded.update({"job", "job_id"})
    view.record({key: value for key, value in result.items() if key not in excluded})
    if "job" in result and result["job"].get("id"):
        job_id = result["job"]["id"]
        view.line("Inspect:")
        view.line(
            f"canvas assignments submissions status {shlex.quote(str(job_id))}",
            exact=True,
        )
    if cleanup:
        view.collection("file_cleanup", cleanup, full=True)


def _render(view: _Pretty, result: dict[str, Any], tool_name: str) -> None:
    if result.get("error"):
        view.line("Error")
        view.record(result, full=True)
    elif tool_name == "get_today":
        view.line(_value(result.get("today")))
        view.record({key: value for key, value in result.items() if key != "today"})
    elif tool_name == "settings_clear":
        view.line("Saved Canvas CLI settings cleared.")
    elif tool_name == "preview_assignment_submission":
        _preview(view, result)
    elif tool_name in {"confirm_assignment_submission", "cancel_scheduled_submission"}:
        _submission(view, result, tool_name)
    elif tool_name == "get_scheduled_submission":
        view.line("Scheduled submission")
        view.job(result["job"])
        view.record(
            {key: value for key, value in result.items() if key not in {"ok", "job"}}
        )
    elif tool_name == "scheduled_fire":
        view.line("Scheduled submission status")
        view.job(result)
    elif tool_name == "list_scheduled_submissions":
        jobs = result.get("jobs", [])
        view.line(f"Scheduled submissions ({len(jobs)} returned)")
        if not jobs:
            view.line("None returned")
        for index, job in enumerate(jobs):
            if index:
                view.line()
            view.job(job)
        view.record(
            {
                key: value
                for key, value in result.items()
                if key not in {"ok", "count", "jobs"}
            }
        )
    else:
        if tool_name == "get_course_context_snapshot" and result.get("errors"):
            view.line("PARTIAL RESULT")
        if tool_name == "get_course_grade_summary":
            view.line("Grades — raw points and group contributions are estimates")
        kind = "auth" if tool_name == "auth_status" else ""
        view.record(result, kind=kind)


def emit(
    result: dict[str, Any],
    *,
    tool_name: str = "",
    failures: bool = True,
    exit_code: int = 1,
) -> None:
    failed = failures and (bool(result.get("error")) or result.get("ok") is False)
    if output_mode() == OutputMode.json:
        sys.stdout.write(
            json.dumps(result, default=str, ensure_ascii=False, separators=(",", ":"))
            + "\n"
        )
    else:
        view = _Pretty(Console(stderr=failed))
        _render(view, result, tool_name)
        if view.omitted:
            view.line("Additional metadata available with canvas --output json …")
    if failed:
        raise typer.Exit(exit_code)


def fail(code: str, message: str, *, exit_code: int = 1, **details: Any) -> None:
    emit({"error": code, "message": message, **details}, exit_code=exit_code)
