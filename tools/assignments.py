from __future__ import annotations

from typing import Any

from auth import CanvasAPIError
from tools.common import (
    canvas_client,
    extract_discussion_topic_id,
    short_canvas_id,
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

    include_submission = bool(args.get("include_submission", False))
    limit = int(args.get("limit", 100))
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


def _peer_rubric_feedback(
    assessments: list[dict[str, Any]],
    *,
    rubric: list[dict[str, Any]],
    anonymous: bool,
) -> list[dict[str, Any]]:
    descriptions = {str(item.get("id")): item.get("description") for item in rubric}
    result = []
    for assessment in assessments:
        if not isinstance(assessment, dict) or assessment.get("assessment_type") != "peer_review":
            continue
        assessor = assessment.get("assessor")
        user = assessor.get("user") if isinstance(assessor, dict) else None
        name = user.get("name") if isinstance(user, dict) and not anonymous else None
        criteria = [
            {
                "criterion_id": str(row.get("criterion_id", "")),
                "description": descriptions.get(str(row.get("criterion_id", ""))),
                "comments": row.get("comments"),
                "points": row.get("points"),
                "rating": row.get("description"),
            }
            for row in assessment.get("data") or []
            if isinstance(row, dict)
        ]
        result.append({"reviewer": name or f"Reviewer {len(result) + 1}", "criteria": criteria})
    return result


def get_assignment_rubric(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()

    include_assessment = bool(args.get("include_assessment", False))
    include_peer_reviews = bool(args.get("include_peer_reviews", False))
    client = canvas_client()
    assignment = client.get_assignment(
        course_id=course_id,
        assignment_id=assignment_id,
        include_submission=include_assessment or include_peer_reviews,
        include_discussion_topic=False,
    )

    assignment_id_value = str(assignment.get("id", ""))
    api_assignment_id = short_canvas_id(assignment_id_value or assignment_id)
    submission = assignment.get("submission")
    if not isinstance(submission, dict):
        submission = None
    assessment = submission.get("rubric_assessment") if submission else None
    assessment_source = "assignment_submission" if assessment is not None else None

    needs_assessment = include_assessment and assessment is None
    needs_user_id = include_peer_reviews and not (submission and submission.get("user_id"))
    if needs_assessment or needs_user_id:
        submissions = client.list_submissions(
            course_id=course_id,
            student_id="self",
            assignment_ids=[api_assignment_id],
            include=["rubric_assessment"] if needs_assessment else None,
            grouped=False,
            limit=1,
        )
        if submissions:
            submission = submissions[0]
            if needs_assessment:
                assessment = submission.get("rubric_assessment")
                if assessment is not None:
                    assessment_source = "submissions_api"

    rubric = assignment.get("rubric") or []
    result = {
        "course_id": course_id,
        "assignment_id": assignment_id_value,
        "assignment_name": assignment.get("name", "Untitled assignment"),
        "points_possible": assignment.get("points_possible"),
        "html_url": assignment.get("html_url"),
        "use_rubric_for_grading": assignment.get("use_rubric_for_grading"),
        "rubric_settings": assignment.get("rubric_settings"),
        "criteria_count": len(rubric) if isinstance(rubric, list) else 0,
        "rubric": rubric,
        "rubric_assessment": assessment,
        "assessment_source": assessment_source,
    }
    if include_peer_reviews:
        result["peer_rubric_assessments"] = []
        result["peer_assessment_source"] = None
        user_id = submission.get("user_id") if submission else None
        if user_id:
            try:
                assessments = client.get_submission_page_rubric_assessments(
                    course_id=course_id,
                    assignment_id=api_assignment_id,
                    student_id=str(user_id),
                )
                result["peer_rubric_assessments"] = _peer_rubric_feedback(
                    assessments,
                    rubric=rubric,
                    anonymous=bool(assignment.get("anonymous_peer_reviews")),
                )
                result["peer_assessment_source"] = "submission_page"
            except CanvasAPIError as exc:
                result["peer_assessment_error"] = str(exc)
    return result


def list_assignment_groups(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()

    include_assignments = bool(args.get("include_assignments", False))
    include_submission = bool(args.get("include_submission", False))
    limit = int(args.get("limit", 100))
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
