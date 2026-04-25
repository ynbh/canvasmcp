from __future__ import annotations

from typing import Any

from tools.common import (
    canvas_client,
    clamp,
    extract_discussion_topic_id,
    id_aliases,
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
