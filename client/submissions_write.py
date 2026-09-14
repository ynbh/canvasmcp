from __future__ import annotations

from typing import Any

from canvasapi import Canvas
from canvasapi.file import File


def _canvasapi_can_delete_files() -> bool:
    return callable(getattr(File, "delete", None))


class CanvasSubmissionsWriteMixin:
    def upload_submission_file(
        self,
        *,
        course_id: str,
        assignment_id: str,
        path: str,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            assignment = canvas.get_course(course_id).get_assignment(assignment_id)
            ok, payload = assignment.upload_to_submission(
                path, submit_assignment=False
            )
            if not ok:
                raise ValueError(payload)
            return self._public_file_dict(payload)

        return self._call_canvas(
            _load,
            f"upload submission file for assignment {assignment_id} in course {course_id}",
        )

    def submit_assignment(
        self,
        *,
        course_id: str,
        assignment_id: str,
        submission: dict[str, Any],
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            if not isinstance(submission, dict) or "submission_type" not in submission:
                raise ValueError("Dictionary with key 'submission_type' is required.")
            assignment = canvas.get_course(course_id).get_assignment(assignment_id)
            result = assignment.submit(dict(submission))
            return self._item_to_dict(result)

        return self._call_canvas(
            _load,
            f"submit assignment {assignment_id} for course {course_id}",
        )

    def delete_user_file(self, *, file_id: str) -> dict[str, Any]:
        if not _canvasapi_can_delete_files():
            return {
                "skipped": True,
                "file_id": file_id,
                "reason": "installed canvasapi does not support File.delete",
            }

        def _load(canvas: Canvas) -> dict[str, Any]:
            deleted = canvas.get_file(file_id).delete()
            return self._public_file_dict(deleted)

        return self._call_canvas(_load, f"delete file {file_id}")

    def _public_file_dict(self, payload: Any) -> dict[str, Any]:
        data = self._item_to_dict(payload)
        display_name = data.get("display_name") or data.get("filename")
        filename = data.get("filename") or data.get("display_name")
        if display_name is not None:
            data["display_name"] = display_name
        if filename is not None:
            data["filename"] = filename
        return data
