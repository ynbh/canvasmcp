from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import re
from typing import Any

from auth import CanvasAPIError, get_auth_status
from schedule.caffeinate import start_caffeinate, stop_caffeinate
from schedule.fire import CANCEL_LOCK_TIMEOUT_SECONDS, cancel_job, delete_uploaded_files
from schedule.launchd import bootout_job, install_job
from schedule.notify import notify
from schedule.store import (
    JOB_STATUSES,
    JobLockTimeout,
    consume_preview,
    create_job,
    delete_job,
    get_job,
    get_pending_job,
    job_lock,
    list_jobs,
    load_preview,
    parse_submit_at,
    save_preview,
)
from tools.common import (
    canvas_api_tool_error,
    canvas_client,
    invalid_argument,
    missing_argument,
    tool_error,
)

SUBMISSION_TYPES = frozenset({"online_upload", "online_text_entry"})
BODY_PREVIEW_LIMIT = 240
_OFFSET_RE = re.compile(r"(Z|z|[+-]\d{2}:?\d{2})$")

SLEEP_WARNING = (
    "Sleep, shutdown, or crash before submit_at means this will not submit. "
    "You can ignore this warning if you know the machine will stay on. "
    "Pass caffeinate=true (CLI: --caffeinate) on confirm to keep the Mac awake "
    "until fire finishes."
)
RESUBMIT_WARNING = "A current attempt exists. Confirming will submit a new attempt."
_REFUSE_MESSAGES = {
    "bad_submission_type": "Assignment does not accept this submission type",
    "bad_extension": "A file extension is not in allowed_extensions",
    "missing_file": "A file path is missing or not readable",
    "locked": "Assignment is locked",
    "past_submit_at": "submit_at is in the past",
    "after_lock_at": "submit_at is after lock_at",
    "attempts_exhausted": "No attempts remaining",
    "auth_not_verified": "Canvas auth is not verified",
    "missing_due_at": "Assignment has no due_at; cannot resolve minutes_before_due",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _has_offset(value: str) -> bool:
    return bool(_OFFSET_RE.search(value.strip()))


def _body_preview(body: Any) -> str | None:
    if body is None:
        return None
    return str(body)[:BODY_PREVIEW_LIMIT]


def _auth_status() -> dict[str, Any]:
    try:
        return get_auth_status()
    except Exception as exc:
        return {
            "auth_verified": False,
            "auth_status": "probe_failed",
            "error": str(exc),
        }


def _override_warning(job: dict[str, Any]) -> str:
    job_id = job.get("id") or "unknown"
    return (
        f"Pending job {job_id} exists for this assignment. "
        "Confirm with override=true to cancel it and arm the new job."
    )


def _current_attempt(submission: Any) -> dict[str, Any] | None:
    if not isinstance(submission, dict):
        return None
    attempt = submission.get("attempt")
    submitted_at = submission.get("submitted_at")
    has_attempt = False
    if attempt is not None:
        try:
            has_attempt = int(attempt) > 0
        except (TypeError, ValueError):
            has_attempt = False
    if not submitted_at and not has_attempt:
        return None
    attachments: list[dict[str, Any]] = []
    for attachment in submission.get("attachments") or []:
        if not isinstance(attachment, dict):
            continue
        attachments.append(
            {
                "id": attachment.get("id"),
                "display_name": attachment.get("display_name")
                or attachment.get("filename"),
                "filename": attachment.get("filename")
                or attachment.get("display_name"),
                "size": attachment.get("size"),
            }
        )
    return {
        "attempt": attempt,
        "submitted_at": submitted_at,
        "submission_type": submission.get("submission_type"),
        "attachments": attachments,
        "body_preview": _body_preview(submission.get("body")),
    }


def _attempts_exhausted(assignment: dict[str, Any]) -> bool:
    allowed = assignment.get("allowed_attempts")
    if allowed is None:
        return False
    try:
        allowed_n = int(allowed)
    except (TypeError, ValueError):
        return False
    if allowed_n < 0:
        return False
    submission = assignment.get("submission")
    attempt = 0
    if isinstance(submission, dict) and submission.get("attempt") is not None:
        try:
            attempt = int(submission["attempt"])
        except (TypeError, ValueError):
            attempt = 0
    return attempt >= allowed_n


def _inspect_file(raw_path: str) -> dict[str, Any]:
    path = Path(raw_path).expanduser()
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    exists = resolved.is_file()
    readable = exists and os.access(resolved, os.R_OK)
    size = resolved.stat().st_size if exists else None
    return {
        "path": str(resolved),
        "filename": resolved.name,
        "size": size,
        "exists": exists,
        "readable": readable,
        "suffix": resolved.suffix.lstrip(".").lower(),
    }


def _planned_payload(
    submission_type: str,
    file_paths: list[str],
    body: str | None,
) -> dict[str, Any]:
    if submission_type == "online_text_entry":
        return {
            "submission_type": submission_type,
            "body_preview": _body_preview(body),
        }
    files = []
    for raw in file_paths:
        info = _inspect_file(raw)
        files.append(
            {
                "path": info["path"],
                "filename": info["filename"],
                "size": info["size"],
            }
        )
    return {"submission_type": submission_type, "files": files}


def _clock_args(args: dict[str, Any]) -> tuple[bool, str | None, int | None]:
    now = bool(args.get("now", False))
    submit_at = str(args.get("submit_at", "")).strip() or None
    minutes_raw = args.get("minutes_before_due")
    minutes: int | None
    if minutes_raw is None or minutes_raw == "":
        minutes = None
    else:
        minutes = int(minutes_raw)
    return now, submit_at, minutes


def _validate_clock_choice(
    now: bool, submit_at: str | None, minutes_before_due: int | None
) -> dict[str, Any] | None:
    chosen = sum([now, submit_at is not None, minutes_before_due is not None])
    if chosen == 0:
        return invalid_argument(
            "must pick a clock: now, submit_at, or minutes_before_due"
        )
    if chosen > 1:
        return invalid_argument(
            "now, submit_at, and minutes_before_due are mutually exclusive"
        )
    if minutes_before_due is not None and minutes_before_due < 0:
        return invalid_argument("minutes_before_due must be >= 0")
    if submit_at is not None and not _has_offset(submit_at):
        return invalid_argument("submit_at must be ISO-8601 with a timezone offset")
    return None


def _resolve_submit_at(
    *,
    now: bool,
    submit_at: str | None,
    minutes_before_due: int | None,
    assignment: dict[str, Any],
) -> tuple[datetime | None, list[str]]:
    if now:
        return None, []
    if submit_at is not None:
        try:
            return parse_submit_at(submit_at), []
        except ValueError:
            return None, ["past_submit_at"]
    due_at = assignment.get("due_at")
    if not due_at:
        return None, ["missing_due_at"]
    try:
        due = parse_submit_at(str(due_at))
    except ValueError:
        return None, ["missing_due_at"]
    minutes = 0 if minutes_before_due is None else minutes_before_due
    return due - timedelta(minutes=minutes), []


def _collect_refuse_reasons(
    *,
    assignment: dict[str, Any],
    submission_type: str,
    file_paths: list[str],
    now: bool,
    submit_at: datetime | None,
    auth_status: dict[str, Any],
    extra: list[str] | None = None,
) -> list[str]:
    reasons: list[str] = []
    for reason in extra or []:
        if reason not in reasons:
            reasons.append(reason)

    allowed_types = assignment.get("submission_types") or []
    if submission_type not in allowed_types:
        reasons.append("bad_submission_type")

    if submission_type == "online_upload":
        allowed_ext = [
            str(item).lstrip(".").lower()
            for item in (assignment.get("allowed_extensions") or [])
            if str(item).strip()
        ]
        for raw in file_paths:
            info = _inspect_file(raw)
            if not info["exists"] or not info["readable"]:
                if "missing_file" not in reasons:
                    reasons.append("missing_file")
                continue
            if allowed_ext and info["suffix"] not in allowed_ext:
                if "bad_extension" not in reasons:
                    reasons.append("bad_extension")

    if assignment.get("locked_for_user") or assignment.get("locked"):
        reasons.append("locked")

    compare_at = _now() if now else submit_at
    if compare_at is not None:
        if not now and compare_at < _now():
            reasons.append("past_submit_at")
        lock_at = assignment.get("lock_at")
        if lock_at:
            try:
                if compare_at > parse_submit_at(str(lock_at)):
                    reasons.append("after_lock_at")
            except ValueError:
                pass

    if _attempts_exhausted(assignment):
        reasons.append("attempts_exhausted")

    if not auth_status.get("auth_verified"):
        reasons.append("auth_not_verified")

    return reasons


def _refuse_message(reasons: list[str]) -> str:
    if not reasons:
        return "Preview refused"
    details = "; ".join(_REFUSE_MESSAGES.get(reason, reason) for reason in reasons)
    return f"Preview refused: {details}"


def _load_assignment(course_id: str, assignment_id: str) -> dict[str, Any]:
    return canvas_client().get_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        include_submission=True,
        include_discussion_topic=False,
    )


def _delete_uploaded_files(file_ids: list[Any]) -> list[dict[str, Any]]:
    if not file_ids:
        return []
    try:
        client = canvas_client()
    except Exception as exc:  # never mask the error that made us clean up
        return [{"file_id": str(file_id), "error": str(exc)} for file_id in file_ids]
    return delete_uploaded_files(file_ids, client)


def _abort(error: dict[str, Any], file_ids: list[str]) -> dict[str, Any]:
    """Return an error after deleting files this confirm uploaded but won't use."""
    return {**error, "file_cleanup": _delete_uploaded_files(file_ids)}


def _upload_files(
    course_id: str,
    assignment_id: str,
    file_paths: list[str],
    *,
    file_ids: list[str],
    filenames: list[str],
) -> None:
    """Upload each file, appending as it goes so a failure leaves the done ones visible."""
    client = canvas_client()
    for raw in file_paths:
        info = _inspect_file(raw)
        uploaded = client.upload_submission_file(
            course_id=course_id,
            assignment_id=assignment_id,
            path=info["path"],
        )
        file_ids.append(str(uploaded.get("id", "")))
        filenames.append(
            str(
                uploaded.get("display_name")
                or uploaded.get("filename")
                or info["filename"]
            )
        )


def _submission_payload(
    submission_type: str, *, file_ids: list[str], body: str | None
) -> dict[str, Any]:
    if submission_type == "online_upload":
        return {"submission_type": "online_upload", "file_ids": file_ids}
    return {"submission_type": "online_text_entry", "body": body or ""}


def preview_assignment_submission(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()
    submission_type = str(args.get("submission_type", "")).strip()
    if not course_id:
        return missing_argument("course_id")
    if not assignment_id:
        return missing_argument("assignment_id")
    if not submission_type:
        return missing_argument("submission_type")
    if submission_type not in SUBMISSION_TYPES:
        return invalid_argument(
            "submission_type must be online_upload or online_text_entry"
        )

    try:
        now, submit_at_raw, minutes_before_due = _clock_args(args)
    except (TypeError, ValueError):
        return invalid_argument("minutes_before_due must be an integer >= 0")
    clock_error = _validate_clock_choice(now, submit_at_raw, minutes_before_due)
    if clock_error is not None:
        return clock_error

    file_paths_raw = args.get("file_paths")
    if file_paths_raw is None:
        file_paths: list[str] = []
    elif not isinstance(file_paths_raw, list):
        return invalid_argument("file_paths must be an array of strings")
    else:
        file_paths = [str(item).strip() for item in file_paths_raw if str(item).strip()]

    body = args.get("body")
    if body is not None:
        body = str(body)

    if submission_type == "online_upload" and not file_paths:
        return missing_argument("file_paths")
    if submission_type == "online_text_entry" and (body is None or body == ""):
        return missing_argument("body")

    try:
        assignment = _load_assignment(course_id, assignment_id)
    except CanvasAPIError as exc:
        return canvas_api_tool_error(exc)

    auth_status = _auth_status()
    pending_job = get_pending_job(course_id, assignment_id)
    submit_at, extra_reasons = _resolve_submit_at(
        now=now,
        submit_at=submit_at_raw,
        minutes_before_due=minutes_before_due,
        assignment=assignment,
    )
    refuse_reasons = _collect_refuse_reasons(
        assignment=assignment,
        submission_type=submission_type,
        file_paths=file_paths,
        now=now,
        submit_at=submit_at,
        auth_status=auth_status,
        extra=extra_reasons,
    )
    current_attempt = _current_attempt(assignment.get("submission"))
    warnings: list[str] = []
    if not now:
        warnings.append(SLEEP_WARNING)
    if pending_job is not None:
        warnings.append(_override_warning(pending_job))
    if current_attempt is not None:
        warnings.append(RESUBMIT_WARNING)

    resolved_paths = [_inspect_file(path)["path"] for path in file_paths]
    preview: dict[str, Any] = {
        "ok": not refuse_reasons,
        "course_id": course_id,
        "assignment_id": assignment_id,
        "assignment_name": assignment.get("name"),
        "due_at": assignment.get("due_at"),
        "lock_at": assignment.get("lock_at"),
        "unlock_at": assignment.get("unlock_at"),
        "submission_types": assignment.get("submission_types") or [],
        "allowed_extensions": assignment.get("allowed_extensions") or [],
        "allowed_attempts": assignment.get("allowed_attempts"),
        "current_attempt": current_attempt,
        "now": now,
        "planned_payload": _planned_payload(submission_type, file_paths, body),
        "auth_status": auth_status,
        "pending_job": pending_job,
        "warnings": warnings,
        "requires_override": pending_job is not None,
    }
    if submit_at is not None:
        preview["submit_at"] = submit_at.isoformat()
    if refuse_reasons:
        preview["refuse_reasons"] = refuse_reasons
        preview["message"] = _refuse_message(refuse_reasons)
        return preview

    record = save_preview(
        {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "assignment_name": assignment.get("name"),
            "submission_type": submission_type,
            "file_paths": resolved_paths,
            "body": body,
            "now": now,
            "submit_at": submit_at.isoformat() if submit_at is not None else None,
            "requires_override": pending_job is not None,
        }
    )
    preview["preview_token"] = record["preview_token"]
    preview["expires_at"] = record["expires_at"]
    return preview


def confirm_assignment_submission(args: dict[str, Any]) -> dict[str, Any]:
    token = str(args.get("preview_token", "")).strip()
    if not token:
        return missing_argument("preview_token")
    override = bool(args.get("override", False))
    caffeinate = bool(args.get("caffeinate", False))

    preview = load_preview(token)
    if preview is None:
        return tool_error(
            "preview_unavailable",
            "Preview token is missing, expired, or already used",
        )

    now = bool(preview.get("now", False))
    if caffeinate and now:
        return invalid_argument("caffeinate cannot be used with now")

    course_id = str(preview.get("course_id", "")).strip()
    assignment_id = str(preview.get("assignment_id", "")).strip()
    submission_type = str(preview.get("submission_type", "")).strip()
    file_paths = [str(path) for path in (preview.get("file_paths") or [])]
    body = preview.get("body")
    if body is not None:
        body = str(body)

    try:
        assignment = _load_assignment(course_id, assignment_id)
    except CanvasAPIError as exc:
        return canvas_api_tool_error(exc)

    auth_status = _auth_status()
    submit_at = None
    extra: list[str] = []
    if not now:
        raw_submit_at = preview.get("submit_at")
        if not raw_submit_at:
            extra.append("past_submit_at")
        else:
            try:
                submit_at = parse_submit_at(str(raw_submit_at))
            except ValueError:
                extra.append("past_submit_at")

    refuse_reasons = _collect_refuse_reasons(
        assignment=assignment,
        submission_type=submission_type,
        file_paths=file_paths,
        now=now,
        submit_at=submit_at,
        auth_status=auth_status,
        extra=extra,
    )
    if refuse_reasons:
        return tool_error(
            "preview_refused",
            _refuse_message(refuse_reasons),
            refuse_reasons=refuse_reasons,
        )

    pending_job = get_pending_job(course_id, assignment_id)
    if pending_job is not None and not override:
        return tool_error(
            "override_required",
            _override_warning(pending_job),
            pending_job=pending_job,
        )

    replacing = pending_job if (pending_job is not None and override) else None
    with ExitStack() as held:
        if replacing is not None:
            # Hold the old job still until the new submit is in place: its fire
            # waits, then finds it cancelled. Taken before the token, so a busy
            # job leaves the token usable for a retry.
            try:
                held.enter_context(
                    job_lock(str(replacing["id"]), timeout=CANCEL_LOCK_TIMEOUT_SECONDS)
                )
            except JobLockTimeout as exc:
                return tool_error("job_busy", str(exc), pending_job=replacing)

        # Claim the token before any side effect: of two concurrent confirms,
        # the loser stops here having changed nothing.
        if consume_preview(token) is None:
            return tool_error(
                "preview_unavailable",
                "Preview token is missing, expired, or already used",
            )

        outcome = _submit_or_schedule(
            course_id=course_id,
            assignment_id=assignment_id,
            assignment_name=preview.get("assignment_name") or assignment.get("name"),
            submission_type=submission_type,
            file_paths=file_paths,
            body=body,
            now=now,
            submit_at=submit_at,
            caffeinate=caffeinate,
        )
        # Only replace the old job once the new one is in place; on failure it
        # stays pending so the assignment is not left with nothing scheduled.
        if outcome.get("ok") and replacing is not None:
            replaced = cancel_job(str(replacing["id"]))
            outcome["file_cleanup"] = list(replaced.get("file_cleanup") or [])
        return outcome


def _discard_job(job_id: str) -> None:
    """Undo a job that was recorded but never armed."""
    stop_caffeinate(job_id)
    bootout_job(job_id)
    delete_job(job_id)


def _submit_or_schedule(
    *,
    course_id: str,
    assignment_id: str,
    assignment_name: Any,
    submission_type: str,
    file_paths: list[str],
    body: str | None,
    now: bool,
    submit_at: datetime | None,
    caffeinate: bool,
) -> dict[str, Any]:
    file_ids: list[str] = []
    filenames: list[str] = []
    if submission_type == "online_upload":
        try:
            _upload_files(
                course_id,
                assignment_id,
                file_paths,
                file_ids=file_ids,
                filenames=filenames,
            )
        except CanvasAPIError as exc:
            return _abort(canvas_api_tool_error(exc), file_ids)
        except Exception:
            _delete_uploaded_files(file_ids)
            raise

    if now:
        auth_status = _auth_status()
        if not auth_status.get("auth_verified"):
            return _abort(
                tool_error(
                    "auth_not_verified",
                    "Canvas auth is not verified",
                    auth_status=auth_status,
                ),
                file_ids,
            )
        try:
            submission = canvas_client().submit_assignment(
                course_id=course_id,
                assignment_id=assignment_id,
                submission=_submission_payload(
                    submission_type, file_ids=file_ids, body=body
                ),
            )
        except CanvasAPIError as exc:
            # Kept, not deleted: Canvas may have accepted the submission anyway.
            return {**canvas_api_tool_error(exc), "uploaded_file_ids": file_ids}
        notify(f"Submitted {assignment_name}")
        return {
            "ok": True,
            "now": True,
            "course_id": course_id,
            "assignment_id": assignment_id,
            "submission": submission,
            "file_cleanup": [],
        }

    assert submit_at is not None
    if submit_at <= _now():
        # Slow uploads can eat the gap between preview and submit_at.
        return _abort(
            tool_error(
                "preview_refused",
                _refuse_message(["past_submit_at"]),
                refuse_reasons=["past_submit_at"],
            ),
            file_ids,
        )

    # Record, then keep awake, then arm launchd last: by the time a fire can
    # run, the job record and its caffeinate pid already exist.
    warnings = [] if caffeinate else [SLEEP_WARNING]
    job_id: str | None = None
    try:
        job = create_job(
            course_id=course_id,
            assignment_id=assignment_id,
            submission_type=submission_type,
            submit_at=submit_at,
            assignment_name=assignment_name,
            file_ids=file_ids,
            filenames=filenames,
            body=body if submission_type == "online_text_entry" else None,
            caffeinate=caffeinate,
        )
        job_id = str(job["id"])
        if caffeinate:
            try:
                start_caffeinate(job_id)
            except OSError as exc:
                warnings = [f"Could not start caffeinate ({exc}). {SLEEP_WARNING}"]
        install_job(job_id, job["submit_at"])
    except Exception as exc:
        if job_id is not None:
            _discard_job(job_id)
        return _abort(
            tool_error("schedule_failed", f"Could not schedule the submit: {exc}"),
            file_ids,
        )
    job = get_job(job_id) or job
    return {
        "ok": True,
        "now": False,
        "job_id": job_id,
        "job": job,
        "warnings": warnings,
        "file_cleanup": [],
    }


def list_scheduled_submissions(args: dict[str, Any]) -> dict[str, Any]:
    status = args.get("status")
    if status is not None:
        status = str(status).strip() or None
        if status is not None and status not in JOB_STATUSES:
            allowed = ", ".join(sorted(JOB_STATUSES))
            return invalid_argument(f"status must be one of: {allowed}")
    jobs = list_jobs(status=status)
    return {"ok": True, "count": len(jobs), "jobs": jobs}


def get_scheduled_submission(args: dict[str, Any]) -> dict[str, Any]:
    job_id = str(args.get("job_id", "")).strip()
    if not job_id:
        return missing_argument("job_id")
    job = get_job(job_id)
    if job is None:
        return tool_error("not_found", f"No scheduled job {job_id}")
    return {"ok": True, "job": job}


def cancel_scheduled_submission(args: dict[str, Any]) -> dict[str, Any]:
    job_id = str(args.get("job_id", "")).strip()
    if not job_id:
        return missing_argument("job_id")
    job = get_job(job_id)
    if job is None:
        return tool_error("not_found", f"No scheduled job {job_id}")
    if job.get("status") != "pending":
        return tool_error(
            "invalid_argument",
            "Only pending jobs can be cancelled",
            job=job,
        )
    try:
        cancelled = cancel_job(job_id)
    except JobLockTimeout as exc:
        return tool_error("job_busy", str(exc), job=job)
    if cancelled.get("status") != "cancelled":
        # A fire got there first; report what actually happened.
        return tool_error(
            "invalid_argument",
            "Only pending jobs can be cancelled",
            job=cancelled,
        )
    return {
        "ok": True,
        "job": cancelled,
        "file_cleanup": list(cancelled.get("file_cleanup") or []),
    }
