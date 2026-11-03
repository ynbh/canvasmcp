from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote

from canvasapi import Canvas

from .base import MAX_PER_PAGE


_JSON = json.JSONDecoder()


def _rubric_assessments_from_html(page: str) -> list[dict[str, Any]]:
    """Extract the rubricAssessments array Canvas embeds in a submission page."""
    for match in re.finditer(r'"rubricAssessments"\s*:\s*', page):
        try:
            value, _ = _JSON.raw_decode(page, match.end())
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and all(
            isinstance(item, dict) and "rubric_assessment" in item for item in value
        ):
            return [item["rubric_assessment"] for item in value]
    raise ValueError("Canvas submission page did not contain rubric assessments")


class CanvasAssignmentsMixin:
    def get_submission_page_rubric_assessments(
        self,
        *,
        course_id: str,
        assignment_id: str,
        student_id: str,
    ) -> list[dict[str, Any]]:
        """Read every rubric assessment embedded in the authenticated submission page.

        Canvas's submissions API omits peer assessments for students, but the
        submission page carries them in its JS environment.
        """

        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            path = "/".join(
                quote(str(part), safe="")
                for part in ("courses", course_id, "assignments", assignment_id, "submissions", student_id)
            )
            with self._web_get(canvas, f"/{path}") as response:
                page = response.text
            return _rubric_assessments_from_html(page)

        return self._call_canvas(
            _load,
            f"read submission page rubric assessments for assignment {assignment_id} in course {course_id}",
        )

    def list_assignments(
        self,
        *,
        course_id: str,
        search: str | None = None,
        bucket: str | None = None,
        include_submission: bool = False,
        include_discussion_topic: bool = True,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if search:
                params["search_term"] = search
            if bucket:
                params["bucket"] = bucket
            include: list[str] = []
            if include_discussion_topic:
                include.append("discussion_topic")
            if include_submission:
                include.append("submission")
            if include:
                params["include"] = include
            return self._paginate_list(course.get_assignments(**params), limit=limit)

        return self._call_canvas(_load, f"list assignments for course {course_id}")

    def get_assignment(
        self,
        *,
        course_id: str,
        assignment_id: str,
        include_submission: bool = False,
        include_discussion_topic: bool = True,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {}
            include: list[str] = []
            if include_discussion_topic:
                include.append("discussion_topic")
            if include_submission:
                include.append("submission")
            if include:
                params["include"] = include
            assignment = course.get_assignment(assignment_id, **params)
            return self._item_to_dict(assignment)

        return self._call_canvas(
            _load,
            f"get assignment {assignment_id} for course {course_id}",
        )

    def list_assignment_groups(
        self,
        *,
        course_id: str,
        include_assignments: bool = False,
        include_submission: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            include: list[str] = []
            if include_assignments:
                include.append("assignments")
            if include_submission:
                include.append("submission")
            if include:
                params["include"] = include
            groups = canvas.get_course(course_id).get_assignment_groups(**params)
            return self._paginate_list(groups, limit=limit)

        return self._call_canvas(
            _load,
            f"list assignment groups for course {course_id}",
        )

    def list_submissions(
        self,
        *,
        course_id: str,
        student_id: str = "self",
        assignment_ids: list[str] | None = None,
        include: list[str] | None = None,
        grouped: bool = False,
        workflow_state: str | None = None,
        submitted_since: str | None = None,
        graded_since: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            effective_include = list(include or [])
            for default_include in (
                "assignment",
                "submission_history",
                "submission_comments",
            ):
                if default_include not in effective_include:
                    effective_include.append(default_include)

            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if grouped:
                params["grouped"] = True
            if student_id:
                params["student_ids"] = [student_id]
            if assignment_ids:
                params["assignment_ids"] = assignment_ids
            if effective_include:
                params["include"] = effective_include
            if workflow_state:
                params["workflow_state"] = workflow_state
            if submitted_since:
                params["submitted_since"] = submitted_since
            if graded_since:
                params["graded_since"] = graded_since

            submissions = canvas.get_course(course_id).get_multiple_submissions(**params)
            return self._paginate_list(submissions, limit=limit)

        return self._call_canvas(_load, f"list submissions for course {course_id}")

    def list_enrollments(
        self,
        *,
        course_id: str,
        user_id: str | None = None,
        include: list[str] | None = None,
        enrollment_type: list[str] | None = None,
        state: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if user_id:
                params["user_id"] = user_id
            if include:
                params["include"] = include
            if enrollment_type:
                params["type"] = enrollment_type
            if state:
                params["state"] = state
            enrollments = canvas.get_course(course_id).get_enrollments(**params)
            return self._paginate_list(enrollments, limit=limit)

        return self._call_canvas(_load, f"list enrollments for course {course_id}")
