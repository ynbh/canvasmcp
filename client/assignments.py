from __future__ import annotations

from typing import Any

from canvasapi import Canvas

from .base import MAX_PER_PAGE


class CanvasAssignmentsMixin:
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
