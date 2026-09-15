from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest

from tools.submit import (
    SLEEP_WARNING,
    cancel_scheduled_submission,
    confirm_assignment_submission,
    get_scheduled_submission,
    list_scheduled_submissions,
    preview_assignment_submission,
)

FUTURE_AT = "2099-01-01T12:00:00-04:00"
PAST_AT = "2020-01-01T12:00:00-04:00"


def _assignment(**overrides):
    assignment = {
        "id": "42",
        "name": "Essay",
        "due_at": "2099-12-01T23:59:00Z",
        "lock_at": "2099-12-02T23:59:00Z",
        "unlock_at": None,
        "submission_types": ["online_upload", "online_text_entry"],
        "allowed_extensions": ["pdf", "txt"],
        "allowed_attempts": -1,
        "locked_for_user": False,
        "locked": False,
        "submission": None,
    }
    assignment.update(overrides)
    return assignment


def _auth_ok():
    return {
        "auth_verified": True,
        "auth_status": "verified",
        "auth_mode": "chrome-session",
    }


def _stored_preview(**overrides):
    preview = {
        "preview_token": "tok123",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "course_id": "1",
        "assignment_id": "42",
        "assignment_name": "Essay",
        "submission_type": "online_upload",
        "file_paths": ["/tmp/essay.pdf"],
        "body": None,
        "now": False,
        "submit_at": FUTURE_AT,
        "requires_override": False,
    }
    preview.update(overrides)
    return preview


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    path = tmp_path / "essay.pdf"
    path.write_bytes(b"%PDF-1.4 fake")
    return path


@pytest.fixture
def txt_path(tmp_path: Path) -> Path:
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    return path


@pytest.fixture
def submit_mocks(pdf_path: Path):
    client = mock.MagicMock()
    client.get_assignment.return_value = _assignment()
    client.upload_submission_file.return_value = {
        "id": "99",
        "display_name": "essay.pdf",
        "size": 12,
    }
    client.submit_assignment.return_value = {
        "id": "sub-1",
        "attempt": 1,
        "submitted_at": "2099-01-01T12:00:00Z",
    }
    client.delete_user_file.return_value = {"id": "99", "display_name": "essay.pdf"}

    job = {
        "id": "job1",
        "status": "pending",
        "course_id": "1",
        "assignment_id": "42",
        "assignment_name": "Essay",
        "submission_type": "online_upload",
        "file_ids": ["99"],
        "filenames": ["essay.pdf"],
        "submit_at": FUTURE_AT,
        "caffeinate": False,
    }

    with (
        mock.patch("tools.submit.canvas_client", return_value=client),
        mock.patch("tools.submit.get_auth_status", return_value=_auth_ok()),
        mock.patch("tools.submit.save_preview") as save_preview,
        mock.patch("tools.submit.load_preview") as load_preview,
        mock.patch("tools.submit.consume_preview") as consume_preview,
        mock.patch("tools.submit.get_pending_job", return_value=None),
        mock.patch("tools.submit.create_job", return_value=job) as create_job,
        mock.patch("tools.submit.get_job", return_value=job),
        mock.patch("tools.submit.list_jobs", return_value=[job]),
        mock.patch("tools.submit.install_job") as install_job,
        mock.patch("tools.submit.start_caffeinate") as start_caffeinate,
        mock.patch("tools.submit.notify") as notify_fn,
        mock.patch("tools.submit.cancel_job", return_value={**job, "status": "cancelled"}),
    ):
        save_preview.side_effect = lambda payload, **kwargs: {
            **payload,
            "preview_token": "tok123",
            "expires_at": "2099-01-01T00:00:00+00:00",
        }
        stored = _stored_preview(file_paths=[str(pdf_path)])
        load_preview.return_value = stored
        consume_preview.return_value = stored
        yield {
            "client": client,
            "save_preview": save_preview,
            "load_preview": load_preview,
            "consume_preview": consume_preview,
            "create_job": create_job,
            "install_job": install_job,
            "start_caffeinate": start_caffeinate,
            "notify": notify_fn,
            "job": job,
            "stored": stored,
        }


class TestPreviewAssignmentSubmission:
    def test_requires_ids_and_type(self, submit_mocks):
        assert preview_assignment_submission({})["error"] == "missing_argument"
        assert preview_assignment_submission({"course_id": "1"})["error"] == (
            "missing_argument"
        )
        assert preview_assignment_submission(
            {"course_id": "1", "assignment_id": "42"}
        )["error"] == "missing_argument"

    def test_refuses_when_no_clock(self, submit_mocks, pdf_path):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
            }
        )
        assert result["error"] == "invalid_argument"
        assert "clock" in result["message"]

    def test_clocks_are_mutually_exclusive(self, submit_mocks, pdf_path):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "now": True,
                "submit_at": FUTURE_AT,
            }
        )
        assert result["error"] == "invalid_argument"
        assert "mutually exclusive" in result["message"]

    def test_requires_files_for_upload(self, submit_mocks):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "now": True,
            }
        )
        assert result["error"] == "missing_argument"
        assert "file_paths" in result["message"]

    def test_requires_body_for_text(self, submit_mocks):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_text_entry",
                "now": True,
            }
        )
        assert result["error"] == "missing_argument"
        assert "body" in result["message"]

    def test_success_includes_token_and_sleep_warning(self, submit_mocks, pdf_path):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "submit_at": FUTURE_AT,
            }
        )
        assert result["ok"] is True
        assert result["preview_token"] == "tok123"
        assert result["expires_at"]
        assert result["assignment_name"] == "Essay"
        assert result["current_attempt"] is None
        assert result["requires_override"] is False
        assert SLEEP_WARNING in result["warnings"]
        assert result["planned_payload"]["files"][0]["filename"] == "essay.pdf"
        submit_mocks["save_preview"].assert_called_once()

    def test_now_skips_sleep_warning(self, submit_mocks, pdf_path):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "now": True,
            }
        )
        assert result["ok"] is True
        assert result["now"] is True
        assert SLEEP_WARNING not in result["warnings"]

    def test_minutes_before_due_freezes_submit_at(self, submit_mocks):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_text_entry",
                "body": "done",
                "minutes_before_due": 2,
            }
        )
        assert result["ok"] is True
        submit_at = datetime.fromisoformat(result["submit_at"])
        due = datetime.fromisoformat("2099-12-01T23:59:00+00:00")
        assert submit_at == due - timedelta(minutes=2)

    def test_refuses_bad_type(self, submit_mocks, pdf_path):
        submit_mocks["client"].get_assignment.return_value = _assignment(
            submission_types=["online_text_entry"]
        )
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "now": True,
            }
        )
        assert result["ok"] is False
        assert "preview_token" not in result
        assert "bad_submission_type" in result["refuse_reasons"]
        submit_mocks["save_preview"].assert_not_called()

    def test_refuses_bad_extension(self, submit_mocks, tmp_path):
        bad = tmp_path / "notes.docx"
        bad.write_text("nope")
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(bad)],
                "now": True,
            }
        )
        assert result["ok"] is False
        assert "bad_extension" in result["refuse_reasons"]

    def test_refuses_missing_file(self, submit_mocks, tmp_path):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(tmp_path / "missing.pdf")],
                "now": True,
            }
        )
        assert result["ok"] is False
        assert "missing_file" in result["refuse_reasons"]

    def test_refuses_past_submit_at(self, submit_mocks, pdf_path):
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "submit_at": PAST_AT,
            }
        )
        assert result["ok"] is False
        assert "past_submit_at" in result["refuse_reasons"]

    def test_refuses_after_lock_at(self, submit_mocks, pdf_path):
        submit_mocks["client"].get_assignment.return_value = _assignment(
            lock_at="2098-01-01T00:00:00Z"
        )
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "submit_at": FUTURE_AT,
            }
        )
        assert result["ok"] is False
        assert "after_lock_at" in result["refuse_reasons"]

    def test_refuses_locked(self, submit_mocks, pdf_path):
        submit_mocks["client"].get_assignment.return_value = _assignment(
            locked_for_user=True
        )
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "now": True,
            }
        )
        assert result["ok"] is False
        assert "locked" in result["refuse_reasons"]

    def test_refuses_exhausted_attempts(self, submit_mocks, pdf_path):
        submit_mocks["client"].get_assignment.return_value = _assignment(
            allowed_attempts=1,
            submission={
                "attempt": 1,
                "submitted_at": "2026-01-01T00:00:00Z",
                "submission_type": "online_upload",
                "attachments": [],
                "body": None,
            },
        )
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "now": True,
            }
        )
        assert result["ok"] is False
        assert "attempts_exhausted" in result["refuse_reasons"]

    def test_refuses_unverified_auth(self, submit_mocks, pdf_path):
        with mock.patch(
            "tools.submit.get_auth_status",
            return_value={"auth_verified": False, "auth_status": "no_cookies"},
        ):
            result = preview_assignment_submission(
                {
                    "course_id": "1",
                    "assignment_id": "42",
                    "submission_type": "online_upload",
                    "file_paths": [str(pdf_path)],
                    "now": True,
                }
            )
        assert result["ok"] is False
        assert "auth_not_verified" in result["refuse_reasons"]

    def test_pending_job_requires_override(self, submit_mocks, pdf_path):
        pending = {"id": "oldjob", "status": "pending"}
        with mock.patch("tools.submit.get_pending_job", return_value=pending):
            result = preview_assignment_submission(
                {
                    "course_id": "1",
                    "assignment_id": "42",
                    "submission_type": "online_upload",
                    "file_paths": [str(pdf_path)],
                    "submit_at": FUTURE_AT,
                }
            )
        assert result["ok"] is True
        assert result["requires_override"] is True
        assert result["pending_job"]["id"] == "oldjob"
        assert any("oldjob" in warning for warning in result["warnings"])

    def test_includes_current_attempt_and_resubmit_warning(self, submit_mocks, pdf_path):
        submit_mocks["client"].get_assignment.return_value = _assignment(
            allowed_attempts=3,
            submission={
                "attempt": 1,
                "submitted_at": "2026-01-01T00:00:00Z",
                "submission_type": "online_text_entry",
                "attachments": [{"id": 7, "display_name": "v1.pdf", "size": 10}],
                "body": "first draft",
            },
        )
        result = preview_assignment_submission(
            {
                "course_id": "1",
                "assignment_id": "42",
                "submission_type": "online_upload",
                "file_paths": [str(pdf_path)],
                "now": True,
            }
        )
        assert result["ok"] is True
        assert result["current_attempt"]["attempt"] == 1
        assert result["current_attempt"]["body_preview"] == "first draft"
        assert any("current attempt" in warning.lower() for warning in result["warnings"])


class TestConfirmAssignmentSubmission:
    def test_missing_or_expired_token(self, submit_mocks):
        submit_mocks["load_preview"].return_value = None
        result = confirm_assignment_submission({"preview_token": "gone"})
        assert result["error"] == "preview_unavailable"

    def test_caffeinate_illegal_with_now(self, submit_mocks, pdf_path):
        submit_mocks["load_preview"].return_value = _stored_preview(
            file_paths=[str(pdf_path)], now=True, submit_at=None
        )
        result = confirm_assignment_submission(
            {"preview_token": "tok123", "caffeinate": True}
        )
        assert result["error"] == "invalid_argument"
        submit_mocks["consume_preview"].assert_not_called()

    def test_override_required(self, submit_mocks, pdf_path):
        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        with mock.patch("tools.submit.get_pending_job", return_value=pending):
            result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["error"] == "override_required"
        submit_mocks["consume_preview"].assert_not_called()
        submit_mocks["client"].upload_submission_file.assert_not_called()

    def test_override_cancels_old_job(self, submit_mocks, pdf_path):
        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        with (
            mock.patch("tools.submit.get_pending_job", return_value=pending),
            mock.patch("tools.submit.cancel_job") as cancel_job,
        ):
            result = confirm_assignment_submission(
                {"preview_token": "tok123", "override": True}
            )
        assert result["ok"] is True
        cancel_job.assert_called_once_with("oldjob")
        submit_mocks["client"].delete_user_file.assert_called_once_with(file_id="88")
        submit_mocks["consume_preview"].assert_called_once_with("tok123")

    def test_consumes_token_and_arms_job(self, submit_mocks, pdf_path):
        result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["ok"] is True
        assert result["job_id"] == "job1"
        assert SLEEP_WARNING in result["warnings"]
        submit_mocks["consume_preview"].assert_called_once_with("tok123")
        submit_mocks["client"].upload_submission_file.assert_called_once()
        kwargs = submit_mocks["client"].upload_submission_file.call_args.kwargs
        assert kwargs["path"] == str(pdf_path.resolve())
        submit_mocks["create_job"].assert_called_once()
        submit_mocks["install_job"].assert_called_once()
        submit_mocks["start_caffeinate"].assert_not_called()
        submit_mocks["client"].submit_assignment.assert_not_called()

    def test_now_skips_launchd_and_submits(self, submit_mocks, pdf_path):
        stored = _stored_preview(file_paths=[str(pdf_path)], now=True, submit_at=None)
        submit_mocks["load_preview"].return_value = stored
        submit_mocks["consume_preview"].return_value = stored
        result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["ok"] is True
        assert result["now"] is True
        assert result["submission"]["id"] == "sub-1"
        submit_mocks["client"].submit_assignment.assert_called_once()
        submission = submit_mocks["client"].submit_assignment.call_args.kwargs[
            "submission"
        ]
        assert submission["submission_type"] == "online_upload"
        assert submission["file_ids"] == ["99"]
        submit_mocks["create_job"].assert_not_called()
        submit_mocks["install_job"].assert_not_called()
        submit_mocks["notify"].assert_called_once()

    def test_now_text_submits_body(self, submit_mocks):
        stored = _stored_preview(
            submission_type="online_text_entry",
            file_paths=[],
            body="hello class",
            now=True,
            submit_at=None,
        )
        submit_mocks["load_preview"].return_value = stored
        submit_mocks["consume_preview"].return_value = stored
        result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["ok"] is True
        submit_mocks["client"].upload_submission_file.assert_not_called()
        submission = submit_mocks["client"].submit_assignment.call_args.kwargs[
            "submission"
        ]
        assert submission == {
            "submission_type": "online_text_entry",
            "body": "hello class",
        }

    def test_caffeinate_starts_on_scheduled_confirm(self, submit_mocks):
        result = confirm_assignment_submission(
            {"preview_token": "tok123", "caffeinate": True}
        )
        assert result["ok"] is True
        submit_mocks["start_caffeinate"].assert_called_once_with("job1")
        assert result["warnings"] == []


class TestScheduledJobTools:
    def test_list_and_get(self, submit_mocks):
        listed = list_scheduled_submissions({})
        assert listed["count"] == 1
        assert listed["jobs"][0]["id"] == "job1"

        got = get_scheduled_submission({"job_id": "job1"})
        assert got["ok"] is True
        assert got["job"]["id"] == "job1"

    def test_get_missing(self, submit_mocks):
        with mock.patch("tools.submit.get_job", return_value=None):
            result = get_scheduled_submission({"job_id": "missing"})
        assert result["error"] == "not_found"

    def test_cancel_pending_deletes_files(self, submit_mocks):
        result = cancel_scheduled_submission({"job_id": "job1"})
        assert result["ok"] is True
        submit_mocks["client"].delete_user_file.assert_called_once_with(file_id="99")

    def test_cancel_non_pending_refuses(self, submit_mocks):
        with mock.patch(
            "tools.submit.get_job",
            return_value={"id": "job1", "status": "submitted", "file_ids": []},
        ):
            result = cancel_scheduled_submission({"job_id": "job1"})
        assert result["error"] == "invalid_argument"


class TestSubmitSpecsAndRecommendations:
    def test_fire_is_not_an_mcp_tool(self):
        from specs.registry import TOOL_SPECS

        names = {spec.name for spec in TOOL_SPECS}
        assert "preview_assignment_submission" in names
        assert "confirm_assignment_submission" in names
        assert "list_scheduled_submissions" in names
        assert "get_scheduled_submission" in names
        assert "cancel_scheduled_submission" in names
        assert "fire_scheduled_submission" not in names

    def test_write_tools_not_recommended_for_resources(self):
        from tools.common import recommended_tool_for_resource

        recommended = {
            recommended_tool_for_resource(resource)
            for resource in (
                "assignment",
                "assignment_submission",
                "file",
                "course",
            )
        }
        assert "preview_assignment_submission" not in recommended
        assert "confirm_assignment_submission" not in recommended
        assert "cancel_scheduled_submission" not in recommended
