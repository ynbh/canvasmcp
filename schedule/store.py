from __future__ import annotations

import json
import os
import re
import secrets
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # Windows: scheduling is launchd-only, so there is nothing to race.
    fcntl = None  # type: ignore[assignment]

PREVIEW_TTL = timedelta(minutes=15)
# Every job starts pending and leaves it exactly once; the other statuses are final.
JOB_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"submitted", "missed", "auth_failed", "failed", "cancelled"}),
    "submitted": frozenset(),
    "missed": frozenset(),
    "auth_failed": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}
JOB_STATUSES = frozenset(JOB_TRANSITIONS)
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
    (root / "locks").mkdir(exist_ok=True)
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


def _job_lock_path(job_id: str) -> Path:
    return schedule_root() / "locks" / f"{_safe_id(job_id, kind='job id')}.lock"


class InvalidJobTransition(ValueError):
    pass


class JobLockTimeout(TimeoutError):
    pass


_held_job_locks = threading.local()


@contextmanager
def job_lock(job_id: str, *, timeout: float | None = None) -> Iterator[None]:
    """Hold the job's lock across processes (launchd fire vs. CLI/MCP cancel).

    Re-entrant within a thread. With a timeout, raises JobLockTimeout instead of
    waiting forever on a fire that is stuck talking to Canvas.
    """
    held: dict[str, int] = getattr(_held_job_locks, "counts", None) or {}
    _held_job_locks.counts = held
    path = _job_lock_path(job_id)
    if held.get(job_id):
        held[job_id] += 1
        try:
            yield
        finally:
            held[job_id] -= 1
        return

    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        if fcntl is not None:
            if timeout is None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            else:
                deadline = time.monotonic() + timeout
                while True:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.monotonic() >= deadline:
                            raise JobLockTimeout(f"Scheduled job {job_id} is busy") from None
                        time.sleep(0.1)
        held[job_id] = 1
        try:
            yield
        finally:
            held.pop(job_id, None)
    finally:
        os.close(fd)  # closing the descriptor releases the flock


def _check_transition(current: Any, target: Any) -> None:
    if target not in JOB_STATUSES:
        raise ValueError(f"Invalid job status: {target}")
    if current == target:
        return
    if target not in JOB_TRANSITIONS.get(str(current), frozenset()):
        raise InvalidJobTransition(f"Job cannot move from {current} to {target}")


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
    if not _preview_is_live(record):
        path.unlink(missing_ok=True)
        return None
    return record


def _preview_is_live(record: dict[str, Any]) -> bool:
    expires_at = record.get("expires_at")
    if not expires_at:
        return False
    try:
        expiry = parse_submit_at(expires_at)
    except ValueError:
        return False
    return _now() < expiry


def delete_preview(token: str) -> None:
    try:
        _preview_path(token).unlink(missing_ok=True)
    except ValueError:
        return


def consume_preview(token: str) -> dict[str, Any] | None:
    """Claim a preview token exactly once, even with concurrent confirms."""
    try:
        path = _preview_path(token)
    except ValueError:
        return None
    claimed = path.with_name(f"{path.stem}.{secrets.token_hex(8)}.claimed")
    try:
        # rename is atomic: of several callers racing on one token, only one wins.
        os.rename(path, claimed)
    except FileNotFoundError:
        return None
    try:
        record = _read_json(claimed)
    finally:
        claimed.unlink(missing_ok=True)
    if record is None or not _preview_is_live(record):
        return None
    return record


def new_job_id() -> str:
    return secrets.token_urlsafe(16)


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
    resolved_id = job_id or new_job_id()
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
    """Write fields onto a job. A status change must follow JOB_TRANSITIONS."""
    with job_lock(job_id):
        job = get_job(job_id)
        if job is None:
            raise KeyError(job_id)
        if "status" in fields:
            _check_transition(job.get("status"), fields["status"])
        job.update(_strip_secrets(fields))
        _write_json(_job_path(job_id), job)
        return job


def delete_job(job_id: str) -> None:
    """Remove a job record. Only for jobs that were never armed."""
    with job_lock(job_id):
        _job_path(job_id).unlink(missing_ok=True)


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
