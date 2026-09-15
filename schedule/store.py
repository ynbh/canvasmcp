from __future__ import annotations

import json
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PREVIEW_TTL = timedelta(minutes=15)
JOB_STATUSES = frozenset(
    {"pending", "submitted", "missed", "auth_failed", "failed", "cancelled"}
)
_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_SECRET_KEY_MARKERS = ("cookie", "csrf")
_SECRET_KEYS = frozenset(
    {
        "authorization",
        "canvas_session",
        "content_bytes",
        "file_bytes",
        "file_content",
        "session",
        "session_cookie",
    }
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def parse_submit_at(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def schedule_root() -> Path:
    override = os.environ.get("CANVASMCP_SCHEDULE_DIR", "").strip()
    if override:
        root = Path(override).expanduser()
    else:
        root = (
            Path.home()
            / "Library"
            / "Application Support"
            / "canvasmcp"
            / "scheduled-submits"
        )
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except OSError:
        pass
    (root / "previews").mkdir(exist_ok=True)
    (root / "jobs").mkdir(exist_ok=True)
    return root


def _is_secret_key(key: str) -> bool:
    lowered = key.casefold()
    if lowered in _SECRET_KEYS:
        return True
    return any(marker in lowered for marker in _SECRET_KEY_MARKERS)


def _strip_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_secrets(item)
            for key, item in value.items()
            if not _is_secret_key(str(key))
        }
    if isinstance(value, list):
        return [_strip_secrets(item) for item in value]
    return value


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _strip_secrets(data)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None
    return loaded


def _safe_id(value: str, *, kind: str) -> str:
    token = str(value).strip()
    if not token or not _TOKEN_RE.fullmatch(token):
        raise ValueError(f"Invalid {kind}")
    return token


def _as_iso(value: str | datetime) -> str:
    return parse_submit_at(value).isoformat()


def _preview_path(token: str) -> Path:
    return schedule_root() / "previews" / f"{_safe_id(token, kind='preview token')}.json"


def _job_path(job_id: str) -> Path:
    return schedule_root() / "jobs" / f"{_safe_id(job_id, kind='job id')}.json"


def save_preview(payload: dict[str, Any], *, token: str | None = None) -> dict[str, Any]:
    preview_token = token or secrets.token_urlsafe(32)
    _safe_id(preview_token, kind="preview token")
    now = _now()
    record = _strip_secrets(dict(payload))
    record["preview_token"] = preview_token
    record["created_at"] = now.isoformat()
    record["expires_at"] = (now + PREVIEW_TTL).isoformat()
    _write_json(_preview_path(preview_token), record)
    return record


def load_preview(token: str) -> dict[str, Any] | None:
    try:
        path = _preview_path(token)
    except ValueError:
        return None
    record = _read_json(path)
    if record is None:
        return None
    expires_at = record.get("expires_at")
    if not expires_at:
        path.unlink(missing_ok=True)
        return None
    try:
        expiry = parse_submit_at(expires_at)
    except ValueError:
        path.unlink(missing_ok=True)
        return None
    if _now() >= expiry:
        path.unlink(missing_ok=True)
        return None
    return record


def delete_preview(token: str) -> None:
    try:
        _preview_path(token).unlink(missing_ok=True)
    except ValueError:
        return


def consume_preview(token: str) -> dict[str, Any] | None:
    record = load_preview(token)
    if record is None:
        return None
    delete_preview(token)
    return record


def create_job(
    *,
    course_id: str,
    assignment_id: str,
    submission_type: str,
    submit_at: str | datetime,
    assignment_name: str | None = None,
    file_ids: list[Any] | None = None,
    filenames: list[Any] | None = None,
    body: str | None = None,
    caffeinate: bool = False,
    caffeinate_pid: int | None = None,
    job_id: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    resolved_id = job_id or secrets.token_urlsafe(16)
    _safe_id(resolved_id, kind="job id")
    record = _strip_secrets(
        {
            "id": resolved_id,
            "status": "pending",
            "course_id": str(course_id),
            "assignment_id": str(assignment_id),
            "assignment_name": assignment_name,
            "submission_type": submission_type,
            "file_ids": list(file_ids or []),
            "filenames": list(filenames or []),
            "body": body,
            "submit_at": _as_iso(submit_at),
            "caffeinate": bool(caffeinate),
            "caffeinate_pid": caffeinate_pid,
            "plist_label": f"com.canvasmcp.submit.{resolved_id}",
            "created_at": _now().isoformat(),
            "fired_at": None,
            "result": None,
            "error": None,
            **extra,
        }
    )
    _write_json(_job_path(resolved_id), record)
    return record


def get_job(job_id: str) -> dict[str, Any] | None:
    try:
        return _read_json(_job_path(job_id))
    except ValueError:
        return None


def update_job(job_id: str, **fields: Any) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        raise KeyError(job_id)
    status = fields.get("status", job.get("status"))
    if status not in JOB_STATUSES:
        raise ValueError(f"Invalid job status: {status}")
    job.update(_strip_secrets(fields))
    _write_json(_job_path(job_id), job)
    return job


def list_jobs(*, status: str | None = None) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for path in (schedule_root() / "jobs").glob("*.json"):
        record = _read_json(path)
        if record is None:
            continue
        if status is not None and record.get("status") != status:
            continue
        jobs.append(record)
    jobs.sort(key=lambda item: str(item.get("created_at") or ""))
    return jobs


def get_pending_job(
    course_id: str, assignment_id: str
) -> dict[str, Any] | None:
    wanted_course = str(course_id)
    wanted_assignment = str(assignment_id)
    for job in list_jobs(status="pending"):
        if (
            str(job.get("course_id")) == wanted_course
            and str(job.get("assignment_id")) == wanted_assignment
        ):
            return job
    return None
