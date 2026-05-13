from __future__ import annotations

from typing import Any

from auth import CanvasAPIError
from tools.common import (
    assignment_submission_download_dir,
    assignment_submission_download_path,
    canvas_client,
    clamp,
    download_dir,
    expand_canvas_id,
    id_aliases,
    is_forbidden_message,
    short_canvas_id,
)


def _object_to_public_dict(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return dict(item)
    if not hasattr(item, "__dict__"):
        return {}
    return {
        key: value
        for key, value in vars(item).items()
        if not key.startswith("_") and not key.endswith("_date")
    }


def _attachment_content_type(
    attachment: dict[str, Any], file_info: dict[str, Any]
) -> Any:
    return (
        attachment.get("content_type")
        or attachment.get("content-type")
        or file_info.get("content_type")
        or file_info.get("content-type")
    )


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
            canvas_id = short_canvas_id(str(item))
            if canvas_id and canvas_id not in assignment_ids:
                assignment_ids.append(canvas_id)

    student_id = str(args.get("student_id", "self")).strip() or "self"
    limit = clamp(args.get("limit"), 200)
    try:
        submissions = canvas_client().list_submissions(
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
        if is_forbidden_message(message):
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
                "assignment_id_aliases": id_aliases(
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


def install_assignment_submission_files(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not assignment_id:
        return {"error": "assignment_id is required"}

    api_assignment_id = short_canvas_id(assignment_id)
    canonical_assignment_id = expand_canvas_id(api_assignment_id, course_id=course_id)
    force_refresh = bool(args.get("force_refresh", False))
    client = canvas_client()

    try:
        submissions = client.list_submissions(
            course_id=course_id,
            student_id="self",
            assignment_ids=[api_assignment_id],
            include=None,
            grouped=False,
            limit=1,
        )
    except CanvasAPIError as exc:
        return {"error": str(exc)}

    root = download_dir()
    assignment_dir = assignment_submission_download_dir(
        root, course_id, canonical_assignment_id
    )

    base_response: dict[str, Any] = {
        "course_id": course_id,
        "assignment_id": canonical_assignment_id,
        "submission_id": None,
        "download_dir": str(assignment_dir),
        "count": 0,
        "downloaded_count": 0,
        "already_present_count": 0,
        "skipped_count": 0,
        "error_count": 0,
        "files": [],
        "skipped": [],
        "errors": [],
    }

    if not submissions:
        base_response["message"] = "No submission was returned for this assignment."
        return base_response

    submission = submissions[0]
    submission_id = str(submission.get("id", "") or "self")
    base_response["submission_id"] = submission_id

    attachments = submission.get("attachments") or []
    if not attachments:
        base_response["message"] = "The submission has no attachment files."
        return base_response

    assignment_dir.mkdir(parents=True, exist_ok=True)

    files: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for attachment in attachments:
        attachment_info = _object_to_public_dict(attachment)
        if not attachment_info:
            skipped.append({"reason": "invalid_attachment", "attachment": attachment})
            continue

        file_id = str(attachment_info.get("id", "")).strip()
        if not file_id:
            skipped.append(
                {"reason": "missing_file_id", "attachment": attachment_info}
            )
            continue

        display_name = str(
            attachment_info.get("display_name")
            or attachment_info.get("filename")
            or attachment_info.get("name")
            or f"file_{file_id}"
        )

        try:
            file_info = attachment_info
            can_download_attachment = callable(getattr(attachment, "download", None))
            if not can_download_attachment:
                file_info = client.get_file(course_id=course_id, file_id=file_id)
            display_name = str(
                file_info.get("display_name")
                or file_info.get("filename")
                or display_name
            )
            target_path = assignment_submission_download_path(
                root,
                course_id,
                canonical_assignment_id,
                submission_id,
                file_id,
                display_name,
            )

            if target_path.exists() and force_refresh:
                target_path.unlink()

            if target_path.exists():
                files.append(
                    {
                        "file_id": file_id,
                        "display_name": display_name,
                        "local_path": str(target_path),
                        "size_bytes": target_path.stat().st_size,
                        "content_type": _attachment_content_type(
                            attachment_info, file_info
                        ),
                        "already_present": True,
                        "status": "already_present",
                    }
                )
                continue

            if can_download_attachment:
                attachment.download(str(target_path))
                downloaded = file_info
            else:
                downloaded = client.download_file(
                    course_id=course_id,
                    file_id=file_id,
                    destination_path=str(target_path),
                )
            files.append(
                {
                    "file_id": file_id,
                    "display_name": display_name,
                    "local_path": str(target_path),
                    "size_bytes": target_path.stat().st_size,
                    "content_type": _attachment_content_type(
                        attachment_info, downloaded
                    ),
                    "already_present": False,
                    "status": "downloaded",
                }
            )
        except Exception as exc:
            errors.append(
                {
                    "file_id": file_id,
                    "display_name": display_name,
                    "reason": str(exc),
                    "attachment": attachment_info,
                }
            )

    base_response.update(
        {
            "count": len(files),
            "downloaded_count": sum(
                1 for item in files if item["status"] == "downloaded"
            ),
            "already_present_count": sum(
                1 for item in files if item["status"] == "already_present"
            ),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "files": files,
            "skipped": skipped,
            "errors": errors,
        }
    )
    return base_response
