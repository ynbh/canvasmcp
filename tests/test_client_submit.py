from __future__ import annotations

from unittest import mock

import pytest

from auth import CanvasAPIError
from client import CanvasClient
from client.submissions_write import CanvasSubmissionsWriteMixin


def _patch_canvas(assignment=None, *, canvas=None):
    if canvas is None:
        canvas = mock.MagicMock()
        course = canvas.get_course.return_value
        if assignment is not None:
            course.get_assignment.return_value = assignment
    canvas_cls = mock.MagicMock(return_value=canvas)
    return mock.patch("client.base.Canvas", canvas_cls), canvas


def _write_client() -> CanvasClient:
    return CanvasClient(base_url="https://school.instructure.com")


class TestCanvasClientMixin:
    def test_client_includes_write_mixin(self):
        assert issubclass(CanvasClient, CanvasSubmissionsWriteMixin)


class TestUploadSubmissionFile:
    def test_passes_submit_assignment_false(self):
        assignment = mock.MagicMock()
        assignment.upload_to_submission.return_value = (
            True,
            {
                "id": 99,
                "display_name": "essay.pdf",
                "filename": "essay.pdf",
                "size": 12,
            },
        )
        patcher, canvas = _patch_canvas(assignment)
        with patcher:
            result = _write_client().upload_submission_file(
                course_id="c1",
                assignment_id="a1",
                path="essay.pdf",
            )

        assignment.upload_to_submission.assert_called_once_with(
            "essay.pdf", submit_assignment=False
        )
        _, kwargs = assignment.upload_to_submission.call_args
        assert kwargs["submit_assignment"] is False
        canvas.get_course.assert_called_once_with("c1")
        canvas.get_course.return_value.get_assignment.assert_called_once_with("a1")
        assert result["id"] == 99
        assert result["display_name"] == "essay.pdf"
        assert result["filename"] == "essay.pdf"
        assert result["size"] == 12

    def test_fills_display_name_from_filename(self):
        assignment = mock.MagicMock()
        assignment.upload_to_submission.return_value = (
            True,
            {"id": 5, "filename": "notes.txt", "size": 3},
        )
        patcher, _canvas = _patch_canvas(assignment)
        with patcher:
            result = _write_client().upload_submission_file(
                course_id="c1",
                assignment_id="a1",
                path="notes.txt",
            )

        assert result["display_name"] == "notes.txt"
        assert result["filename"] == "notes.txt"

    def test_raises_canvas_api_error_on_upload_failure(self):
        assignment = mock.MagicMock()
        assignment.upload_to_submission.return_value = (False, {"message": "denied"})
        patcher, _canvas = _patch_canvas(assignment)
        with patcher:
            with pytest.raises(CanvasAPIError, match="upload submission file") as exc_info:
                _write_client().upload_submission_file(
                    course_id="c1",
                    assignment_id="a1",
                    path="essay.pdf",
                )
        assert exc_info.value.status_code is None
        assignment.upload_to_submission.assert_called_once_with(
            "essay.pdf", submit_assignment=False
        )


class TestSubmitAssignment:
    def test_online_upload_with_file_ids(self):
        assignment = mock.MagicMock()
        assignment.submit.return_value = {
            "id": 7,
            "submission_type": "online_upload",
            "attachments": [{"id": 99}],
        }
        patcher, canvas = _patch_canvas(assignment)
        payload = {"submission_type": "online_upload", "file_ids": [99, 100]}
        with patcher:
            result = _write_client().submit_assignment(
                course_id="c1",
                assignment_id="a1",
                submission=payload,
            )

        assignment.submit.assert_called_once_with(
            {"submission_type": "online_upload", "file_ids": [99, 100]}
        )
        submitted = assignment.submit.call_args.args[0]
        assert submitted is not payload
        canvas.get_course.assert_called_once_with("c1")
        assert result["submission_type"] == "online_upload"
        assert result["id"] == 7

    def test_online_text_entry_with_body(self):
        assignment = mock.MagicMock()
        assignment.submit.return_value = {
            "id": 8,
            "submission_type": "online_text_entry",
            "body": "hello world",
        }
        patcher, _canvas = _patch_canvas(assignment)
        with patcher:
            result = _write_client().submit_assignment(
                course_id="c1",
                assignment_id="a1",
                submission={
                    "submission_type": "online_text_entry",
                    "body": "hello world",
                },
            )

        assignment.submit.assert_called_once_with(
            {"submission_type": "online_text_entry", "body": "hello world"}
        )
        assert result["submission_type"] == "online_text_entry"
        assert result["body"] == "hello world"

    def test_requires_submission_type(self):
        assignment = mock.MagicMock()
        patcher, _canvas = _patch_canvas(assignment)
        with patcher:
            with pytest.raises(CanvasAPIError, match="submission_type"):
                _write_client().submit_assignment(
                    course_id="c1",
                    assignment_id="a1",
                    submission={"body": "missing type"},
                )
        assignment.submit.assert_not_called()


class TestDeleteUserFile:
    def test_deletes_via_canvasapi_file(self):
        canvas_file = mock.MagicMock()
        canvas_file.delete.return_value = {
            "id": 99,
            "display_name": "essay.pdf",
            "filename": "essay.pdf",
            "size": 12,
        }
        canvas = mock.MagicMock()
        canvas.get_file.return_value = canvas_file
        patcher, _canvas = _patch_canvas(canvas=canvas)
        with patcher:
            result = _write_client().delete_user_file(file_id="99")

        canvas.get_file.assert_called_once_with("99")
        canvas_file.delete.assert_called_once_with()
        assert result["id"] == 99
        assert result["display_name"] == "essay.pdf"
        assert "skipped" not in result

    def test_skips_when_file_delete_unavailable(self):
        canvas_cls = mock.MagicMock()
        with (
            mock.patch(
                "client.submissions_write._canvasapi_can_delete_files",
                return_value=False,
            ),
            mock.patch("client.base.Canvas", canvas_cls),
        ):
            result = _write_client().delete_user_file(file_id="99")

        assert result == {
            "skipped": True,
            "file_id": "99",
            "reason": "installed canvasapi does not support File.delete",
        }
        canvas_cls.assert_not_called()
