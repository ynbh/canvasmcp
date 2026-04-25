from __future__ import annotations

from typing import Any

from tools.common import canvas_client


def get_course_grade_summary(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    student_id = str(args.get("student_id", "self")).strip() or "self"
    client = canvas_client()
    course = client.get_course(course_id=course_id, include=["term"])
    enrollments = client.list_enrollments(
        course_id=course_id,
        user_id=student_id,
        include=["grades"],
        limit=10,
    )
    enrollment = enrollments[0] if enrollments else {}
    submissions = client.list_submissions(
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

    assignment_groups = client.list_assignment_groups(
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
