from __future__ import annotations

from typing import Any

from auth import CanvasAPIError
from tools.common import (
    canvas_client,
    clamp,
    expand_canvas_id,
    extract_discussion_topic_id,
    id_aliases,
    is_forbidden_message,
)


def _assignment_summary(
    assignment: dict[str, Any],
    *,
    course_id: str,
    include_submission: bool = False,
    keep_submission_key: bool = False,
) -> dict[str, Any]:
    assignment_id = str(assignment.get("id", ""))
    discussion_topic_id = extract_discussion_topic_id(assignment)
    summary = {
        "id": assignment_id,
        "id_aliases": id_aliases(assignment_id, course_id=course_id),
        "name": assignment.get("name", "Untitled assignment"),
        "due_at": assignment.get("due_at"),
        "unlock_at": assignment.get("unlock_at"),
        "lock_at": assignment.get("lock_at"),
        "points_possible": assignment.get("points_possible"),
        "html_url": assignment.get("html_url"),
        "submission_types": assignment.get("submission_types") or [],
        "has_rubric": bool(assignment.get("rubric")),
        "use_rubric_for_grading": assignment.get("use_rubric_for_grading"),
        "discussion_topic_id": discussion_topic_id,
        "discussion_topic_id_aliases": id_aliases(
            str(discussion_topic_id or ""), course_id=course_id
        ),
    }
    if include_submission or keep_submission_key:
        summary["submission"] = assignment.get("submission")
    return summary


def _assignment_details(
    assignment: dict[str, Any],
    *,
    course_id: str,
) -> dict[str, Any]:
    details = _assignment_summary(assignment, course_id=course_id)
    details.update(
        {
            "description": assignment.get("description"),
            "published": assignment.get("published"),
            "grading_type": assignment.get("grading_type"),
            "allowed_extensions": assignment.get("allowed_extensions") or [],
            "has_submitted_submissions": assignment.get("has_submitted_submissions"),
            "rubric": assignment.get("rubric") or [],
            "rubric_settings": assignment.get("rubric_settings"),
            "discussion_topic": assignment.get("discussion_topic")
            if isinstance(assignment.get("discussion_topic"), dict)
            else None,
            "submission": assignment.get("submission"),
        }
    )
    return details


def list_course_assignments(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_submission = bool(args.get("include_submission", False))
    limit = clamp(args.get("limit"), 100)
    assignments = canvas_client().list_assignments(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        bucket=str(args.get("bucket")) if args.get("bucket") else None,
        include_submission=include_submission,
        include_discussion_topic=True,
        limit=limit,
    )
    items = [
        _assignment_summary(
            assignment,
            course_id=course_id,
            include_submission=include_submission,
        )
        for assignment in assignments
    ]
    return {"course_id": course_id, "count": len(items), "assignments": items}


def get_assignment_details(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not assignment_id:
        return {"error": "assignment_id is required"}

    assignment = canvas_client().get_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        include_submission=bool(args.get("include_submission", False)),
        include_discussion_topic=True,
    )

    return {
        "course_id": course_id,
        "assignment": _assignment_details(assignment, course_id=course_id),
    }


def get_assignment_rubric(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not assignment_id:
        return {"error": "assignment_id is required"}

    include_assessment = bool(args.get("include_assessment", False))
    client = canvas_client()
    assignment = client.get_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        include_submission=include_assessment,
        include_discussion_topic=False,
    )

    submission = assignment.get("submission")
    assessment = None
    if isinstance(submission, dict):
        assessment = submission.get("rubric_assessment")

    assignment_id_value = str(assignment.get("id", ""))
    if include_assessment and assessment is None:
        submissions = client.list_submissions(
            course_id=course_id,
            student_id="self",
            assignment_ids=[assignment_id_value or assignment_id],
            include=["rubric_assessment"],
            grouped=False,
            limit=1,
        )
        if submissions:
            assessment = submissions[0].get("rubric_assessment")

    rubric = assignment.get("rubric") or []
    return {
        "course_id": course_id,
        "assignment_id": assignment_id_value,
        "assignment_id_aliases": id_aliases(assignment_id_value, course_id=course_id),
        "assignment_name": assignment.get("name", "Untitled assignment"),
        "points_possible": assignment.get("points_possible"),
        "html_url": assignment.get("html_url"),
        "use_rubric_for_grading": assignment.get("use_rubric_for_grading"),
        "rubric_settings": assignment.get("rubric_settings"),
        "criteria_count": len(rubric) if isinstance(rubric, list) else 0,
        "rubric": rubric,
        "rubric_assessment": assessment,
        "assessment_source": "submission" if assessment is not None else None,
    }


def list_assignment_groups(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_assignments = bool(args.get("include_assignments", False))
    include_submission = bool(args.get("include_submission", False))
    limit = clamp(args.get("limit"), 100)
    groups = canvas_client().list_assignment_groups(
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
                item = _assignment_summary(
                    assignment,
                    course_id=course_id,
                    include_submission=include_submission,
                    keep_submission_key=True,
                )
                assignments.append(item)

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
            canonical_id = expand_canvas_id(str(item), course_id=course_id)
            if canonical_id and canonical_id not in assignment_ids:
                assignment_ids.append(canonical_id)

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


def get_course_grade_summary(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    student_id = str(args.get("student_id", "self")).strip() or "self"
    course = canvas_client().get_course(course_id=course_id, include=["term"])
    enrollments = canvas_client().list_enrollments(
        course_id=course_id,
        user_id=student_id,
        include=["grades"],
        limit=10,
    )
    enrollment = enrollments[0] if enrollments else {}
    submissions = canvas_client().list_submissions(
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

    assignment_groups = canvas_client().list_assignment_groups(
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
            score = submission.get("score") if isinstance(submission, dict) else None
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
