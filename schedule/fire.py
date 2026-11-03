from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from auth import get_auth_status
from schedule.caffeinate import stop_caffeinate
from schedule.launchd import bootout_job
from schedule.notify import notify
from schedule.store import get_job, job_lock, parse_submit_at, update_job


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


# Statuses where Canvas never saw a submit attempt, so the uploaded files are
# orphans. "failed" is left out: a timeout can fail after Canvas accepted the
# submission, and deleting its files then would break the submitted attempt.
_DELETE_FILES_ON = frozenset({"missed", "auth_failed", "cancelled"})
CANCEL_LOCK_TIMEOUT_SECONDS = 30.0


def delete_uploaded_files(file_ids: list[Any], client: Any = None) -> list[dict[str, Any]]:
    """Best-effort delete of files uploaded for a submission that will not happen."""
    if not file_ids:
        return []
    try:
        client = client or canvas_client()
    except Exception as exc:
        return [{"file_id": str(file_id), "error": str(exc)} for file_id in file_ids]
    notes: list[dict[str, Any]] = []
    for file_id in file_ids:
        ident = str(file_id)
        try:
            client.delete_user_file(file_id=ident)
            notes.append({"file_id": ident, "deleted": True})
        except Exception as exc:
            notes.append({"file_id": ident, "error": str(exc)})
    return notes


def _finish(job_id: str, status: str, *, announce: bool = True, **fields: Any) -> dict[str, Any]:
    """Move a pending job to a final status and release what it holds.

    The caller must hold job_lock(job_id) and have seen the job pending.
    Bootout comes last: when this runs inside the launchd fire, booting out the
    job's own label SIGTERMs this process.
    """
    job = update_job(job_id, status=status, **fields)
    stop_caffeinate(job_id)
    if status in _DELETE_FILES_ON and job.get("file_ids"):
        job = update_job(
            job_id, file_cleanup=delete_uploaded_files(list(job["file_ids"]))
        )
    if announce:
        notify(_notify_message(job))
    job = get_job(job_id) or job
    bootout_job(job_id)
    return job


def _auth_verified() -> tuple[bool, str | None]:
    try:
        status = get_auth_status()
    except Exception as exc:
        return False, str(exc)
    if status.get("auth_verified"):
        return True, None
    return False, str(status.get("error") or "Canvas auth is not verified")


def fire_job(job_id: str) -> dict[str, Any]:
    if get_job(job_id) is None:
        return {"error": "not_found", "message": f"No scheduled job {job_id}"}
    # Held through the submit so a concurrent cancel waits, then sees the outcome.
    with job_lock(job_id):
        job = get_job(job_id)
        if job is None:
            return {"error": "not_found", "message": f"No scheduled job {job_id}"}
        if job.get("status") != "pending":
            return job

        fired_at = _now().isoformat()
        submit_at = parse_submit_at(job["submit_at"])
        if _now() > submit_at + MISSED_SKEW:
            return _finish(
                job_id,
                "missed",
                fired_at=fired_at,
                error="Fire ran after the 60s window",
            )

        ok, error = _auth_verified()
        if not ok:
            return _finish(job_id, "auth_failed", fired_at=fired_at, error=error)

        try:
            client = canvas_client()
            result = client.submit_assignment(
                course_id=job["course_id"],
                assignment_id=job["assignment_id"],
                submission=_submission_payload(job),
            )
        except Exception as exc:
            return _finish(job_id, "failed", fired_at=fired_at, error=str(exc))

        return _finish(job_id, "submitted", fired_at=fired_at, result=result, error=None)


def cancel_job(job_id: str) -> dict[str, Any]:
    """Cancel a pending job. Returns the job as it ends up; check its status.

    Raises JobLockTimeout if a fire has held the job for too long.
    """
    if get_job(job_id) is None:
        return {"error": "not_found", "message": f"No scheduled job {job_id}"}
    with job_lock(job_id, timeout=CANCEL_LOCK_TIMEOUT_SECONDS):
        job = get_job(job_id)
        if job is None:
            return {"error": "not_found", "message": f"No scheduled job {job_id}"}
        if job.get("status") != "pending":
            return job
        return _finish(job_id, "cancelled", announce=False)
