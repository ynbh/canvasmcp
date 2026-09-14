from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from auth import CanvasAPIError, get_auth_status
from schedule.caffeinate import stop_caffeinate
from schedule.launchd import bootout_job
from schedule.notify import notify
from schedule.store import get_job, parse_submit_at, update_job


def canvas_client():
    from tools.common import canvas_client as _canvas_client

    return _canvas_client()

MISSED_SKEW = timedelta(seconds=60)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _submission_payload(job: dict[str, Any]) -> dict[str, Any]:
    kind = job.get("submission_type")
    if kind == "online_upload":
        return {
            "submission_type": "online_upload",
            "file_ids": list(job.get("file_ids") or []),
        }
    if kind == "online_text_entry":
        return {
            "submission_type": "online_text_entry",
            "body": job.get("body") or "",
        }
    raise ValueError(f"Unsupported submission_type: {kind}")


def _notify_message(job: dict[str, Any]) -> str:
    name = job.get("assignment_name") or f"assignment {job.get('assignment_id')}"
    status = job.get("status")
    if status == "submitted":
        return f"Submitted {name}"
    if status == "missed":
        return f"Missed scheduled submit for {name}"
    if status == "auth_failed":
        return f"Auth failed for scheduled submit: {name}"
    if status == "failed":
        error = job.get("error") or "unknown error"
        return f"Scheduled submit failed for {name}: {error}"
    return f"Scheduled submit {status}: {name}"


def _finish(job_id: str, **fields: Any) -> dict[str, Any]:
    fields.setdefault("fired_at", _now().isoformat())
    job = update_job(job_id, **fields)
    try:
        notify(_notify_message(job))
    except Exception:
        pass
    bootout_job(job_id)
    stop_caffeinate(job_id)
    return get_job(job_id) or job


def _auth_verified() -> tuple[bool, str | None]:
    try:
        status = get_auth_status()
    except Exception as exc:
        return False, str(exc)
    if status.get("auth_verified"):
        return True, None
    return False, str(status.get("error") or "Canvas auth is not verified")


def fire_job(job_id: str) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        return {"error": "not_found", "message": f"No scheduled job {job_id}"}
    if job.get("status") != "pending":
        return job

    submit_at = parse_submit_at(job["submit_at"])
    if _now() > submit_at + MISSED_SKEW:
        return _finish(job_id, status="missed", error="Fire ran after the 60s window")

    ok, error = _auth_verified()
    if not ok:
        return _finish(job_id, status="auth_failed", error=error)

    try:
        client = canvas_client()
        result = client.submit_assignment(
            course_id=job["course_id"],
            assignment_id=job["assignment_id"],
            submission=_submission_payload(job),
        )
    except CanvasAPIError as exc:
        return _finish(job_id, status="failed", error=str(exc))
    except Exception as exc:
        return _finish(job_id, status="failed", error=str(exc))

    return _finish(job_id, status="submitted", result=result, error=None)


def cancel_job(job_id: str) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        return {"error": "not_found", "message": f"No scheduled job {job_id}"}
    if job.get("status") != "pending":
        return job
    bootout_job(job_id)
    stop_caffeinate(job_id)
    return update_job(job_id, status="cancelled")
