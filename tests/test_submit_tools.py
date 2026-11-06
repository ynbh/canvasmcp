from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest
import requests

from auth import CanvasAPIError
from client import CanvasClient
from tools.submit import (
    SLEEP_WARNING,
    cancel_scheduled_submission,
    confirm_assignment_submission,
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
    client = mock.create_autospec(CanvasClient, instance=True)
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
        mock.patch("schedule.fire.canvas_client", return_value=client),
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
        mock.patch("tools.submit.stop_caffeinate") as stop_caffeinate,
        mock.patch("tools.submit.bootout_job") as bootout_job,
        mock.patch("tools.submit.delete_job") as delete_job,
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
            "stop_caffeinate": stop_caffeinate,
            "bootout_job": bootout_job,
            "delete_job": delete_job,
            "notify": notify_fn,
            "job": job,
            "stored": stored,
        }


class TestPreviewAssignmentSubmission:
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

    def test_override_cancels_old_job_only_after_new_one_is_armed(
        self, submit_mocks, pdf_path
    ):
        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        cleanup = [{"file_id": "88", "deleted": True}]
        order = mock.Mock()
        order.attach_mock(submit_mocks["consume_preview"], "consume")
        order.attach_mock(submit_mocks["install_job"], "install")
        with (
            mock.patch("tools.submit.get_pending_job", return_value=pending),
            mock.patch(
                "tools.submit.cancel_job",
                return_value={**pending, "status": "cancelled", "file_cleanup": cleanup},
            ) as cancel_job,
        ):
            order.attach_mock(cancel_job, "cancel")
            result = confirm_assignment_submission(
                {"preview_token": "tok123", "override": True}
            )
        assert result["ok"] is True
        assert result["file_cleanup"] == cleanup
        assert [name for name, *_ in order.mock_calls] == ["consume", "install", "cancel"]

    def test_override_keeps_old_job_when_new_one_fails(self, submit_mocks, pdf_path):
        from auth import CanvasAPIError

        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        submit_mocks["client"].upload_submission_file.side_effect = CanvasAPIError("boom")
        with (
            mock.patch("tools.submit.get_pending_job", return_value=pending),
            mock.patch("tools.submit.cancel_job") as cancel_job,
        ):
            result = confirm_assignment_submission(
                {"preview_token": "tok123", "override": True}
            )
        assert result["error"]
        cancel_job.assert_not_called()

    def test_busy_old_job_leaves_token_usable(self, submit_mocks, pdf_path):
        from schedule.store import JobLockTimeout

        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        with (
            mock.patch("tools.submit.get_pending_job", return_value=pending),
            mock.patch("tools.submit.job_lock", side_effect=JobLockTimeout("busy")),
        ):
            result = confirm_assignment_submission(
                {"preview_token": "tok123", "override": True}
            )
        assert result["error"] == "job_busy"
        submit_mocks["consume_preview"].assert_not_called()
        submit_mocks["client"].upload_submission_file.assert_not_called()

    def test_old_job_that_fired_while_waiting_is_not_replaced(self, submit_mocks, pdf_path):
        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        fired = {**pending, "status": "submitted"}
        with (
            mock.patch("tools.submit.get_pending_job", return_value=pending),
            mock.patch("tools.submit.get_job", return_value=fired),
            mock.patch("tools.submit.cancel_job") as cancel_job,
        ):
            result = confirm_assignment_submission(
                {"preview_token": "tok123", "override": True}
            )
        assert result["error"] == "invalid_argument"
        assert result["job"]["status"] == "submitted"
        submit_mocks["consume_preview"].assert_not_called()
        submit_mocks["client"].upload_submission_file.assert_not_called()
        cancel_job.assert_not_called()

    def test_lost_token_claim_changes_nothing(self, submit_mocks, pdf_path):
        pending = {"id": "oldjob", "status": "pending", "file_ids": ["88"]}
        submit_mocks["consume_preview"].return_value = None
        with (
            mock.patch("tools.submit.get_pending_job", return_value=pending),
            mock.patch("tools.submit.cancel_job") as cancel_job,
        ):
            result = confirm_assignment_submission(
                {"preview_token": "tok123", "override": True}
            )
        assert result["error"] == "preview_unavailable"
        cancel_job.assert_not_called()
        submit_mocks["client"].upload_submission_file.assert_not_called()

    @pytest.mark.parametrize(
        "exc",
        [CanvasAPIError("upload broke", status_code=500), requests.ConnectionError("reset")],
    )
    def test_partial_upload_failure_deletes_uploaded_files(
        self, submit_mocks, pdf_path, txt_path, exc
    ):
        stored = _stored_preview(file_paths=[str(pdf_path), str(txt_path)])
        submit_mocks["load_preview"].return_value = stored
        submit_mocks["consume_preview"].return_value = stored
        submit_mocks["client"].upload_submission_file.side_effect = [
            {"id": "99", "display_name": "essay.pdf"},
            exc,
        ]
        result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["error"] in {"canvas_api_error", "internal_error"}
        assert result["file_cleanup"] == [{"file_id": "99", "deleted": True}]
        submit_mocks["client"].delete_user_file.assert_called_once_with(file_id="99")
        submit_mocks["create_job"].assert_not_called()
        submit_mocks["install_job"].assert_not_called()

    def test_now_auth_recheck_failure_deletes_uploaded_files(self, submit_mocks, pdf_path):
        stored = _stored_preview(file_paths=[str(pdf_path)], now=True, submit_at=None)
        submit_mocks["load_preview"].return_value = stored
        submit_mocks["consume_preview"].return_value = stored
        with mock.patch(
            "tools.submit.get_auth_status",
            side_effect=[_auth_ok(), {"auth_verified": False}],
        ):
            result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["error"] == "auth_not_verified"
        submit_mocks["client"].submit_assignment.assert_not_called()
        submit_mocks["client"].delete_user_file.assert_called_once_with(file_id="99")

    @pytest.mark.parametrize(
        "exc",
        [
            CanvasAPIError("timeout"),
            requests.ConnectionError("connection reset"),
            requests.Timeout("read timed out"),
        ],
    )
    def test_now_submit_failure_keeps_uploaded_files(self, submit_mocks, pdf_path, exc):
        stored = _stored_preview(file_paths=[str(pdf_path)], now=True, submit_at=None)
        submit_mocks["load_preview"].return_value = stored
        submit_mocks["consume_preview"].return_value = stored
        submit_mocks["client"].submit_assignment.side_effect = exc
        result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["error"] in {"canvas_api_error", "internal_error"}
        assert result["uploaded_file_ids"] == ["99"]
        submit_mocks["client"].delete_user_file.assert_not_called()

    def test_install_failure_discards_job_and_cleans_up(self, submit_mocks, pdf_path):
        submit_mocks["install_job"].side_effect = FileNotFoundError(
            "canvas executable not found on PATH"
        )
        result = confirm_assignment_submission(
            {"preview_token": "tok123", "caffeinate": True}
        )
        assert result["error"] == "schedule_failed"
        assert "not found on PATH" in result["message"]
        submit_mocks["stop_caffeinate"].assert_called_once_with("job1")
        submit_mocks["bootout_job"].assert_called_once_with("job1")
        submit_mocks["delete_job"].assert_called_once_with("job1")
        submit_mocks["client"].delete_user_file.assert_called_once_with(file_id="99")

    def test_record_and_caffeinate_happen_before_launchd_is_armed(self, submit_mocks):
        order = mock.Mock()
        order.attach_mock(submit_mocks["create_job"], "create")
        order.attach_mock(submit_mocks["start_caffeinate"], "caffeinate")
        order.attach_mock(submit_mocks["install_job"], "install")
        result = confirm_assignment_submission(
            {"preview_token": "tok123", "caffeinate": True}
        )
        assert result["ok"] is True
        assert [name for name, *_ in order.mock_calls] == ["create", "caffeinate", "install"]
        assert submit_mocks["install_job"].call_args.args[0] == "job1"

    def test_submit_at_that_passes_during_upload_is_refused(self, submit_mocks, pdf_path):
        import tools.submit as submit_module

        real_now = submit_module._now()
        clock = {"now": real_now}

        def slow_upload(**kwargs):
            clock["now"] = datetime.fromisoformat(FUTURE_AT) + timedelta(seconds=1)
            return {"id": "99", "display_name": "essay.pdf"}

        submit_mocks["client"].upload_submission_file.side_effect = slow_upload
        with mock.patch("tools.submit._now", side_effect=lambda: clock["now"]):
            result = confirm_assignment_submission({"preview_token": "tok123"})
        assert result["refuse_reasons"] == ["past_submit_at"]
        submit_mocks["create_job"].assert_not_called()
        submit_mocks["install_job"].assert_not_called()
        submit_mocks["client"].delete_user_file.assert_called_once_with(file_id="99")

    def test_cleanup_failure_does_not_mask_the_original_error(
        self, submit_mocks, pdf_path, txt_path
    ):
        from auth import CanvasAPIError

        stored = _stored_preview(file_paths=[str(pdf_path), str(txt_path)])
        submit_mocks["load_preview"].return_value = stored
        submit_mocks["consume_preview"].return_value = stored
        real_client = submit_mocks["client"]
        state = {"uploaded": False}

        def failing_upload(**kwargs):
            if not state["uploaded"]:
                state["uploaded"] = True
                return {"id": "99", "display_name": "essay.pdf"}
            raise CanvasAPIError("boom")

        real_client.upload_submission_file.side_effect = failing_upload

        def flaky_client():
            if state["uploaded"]:
                raise RuntimeError("no client")
            return real_client

        with (
            mock.patch("tools.submit.canvas_client", side_effect=flaky_client),
            mock.patch("schedule.fire.canvas_client", side_effect=flaky_client),
        ):
            result = confirm_assignment_submission({"preview_token": "tok123"})
        assert "boom" in result["message"]
        assert result["file_cleanup"] == [{"file_id": "99", "error": "no client"}]

    def test_caffeinate_failure_still_arms_job(self, submit_mocks):
        submit_mocks["start_caffeinate"].side_effect = FileNotFoundError("caffeinate")
        result = confirm_assignment_submission(
            {"preview_token": "tok123", "caffeinate": True}
        )
        assert result["ok"] is True
        assert "Could not start caffeinate" in result["warnings"][0]

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
    def test_cancel_pending_reports_file_cleanup(self, submit_mocks):
        cleanup = [{"file_id": "99", "deleted": True}]
        job = submit_mocks["job"]
        with mock.patch(
            "tools.submit.cancel_job",
            return_value={**job, "status": "cancelled", "file_cleanup": cleanup},
        ) as cancel_job:
            result = cancel_scheduled_submission({"job_id": "job1"})
        assert result["ok"] is True
        assert result["file_cleanup"] == cleanup
        cancel_job.assert_called_once_with("job1")

    def test_cancel_that_loses_to_fire_reports_outcome(self, submit_mocks):
        job = submit_mocks["job"]
        with mock.patch(
            "tools.submit.cancel_job", return_value={**job, "status": "submitted"}
        ):
            result = cancel_scheduled_submission({"job_id": "job1"})
        assert result["error"] == "invalid_argument"
        assert result["job"]["status"] == "submitted"

    def test_cancel_busy_job(self, submit_mocks):
        from schedule.store import JobLockTimeout

        with mock.patch("tools.submit.cancel_job", side_effect=JobLockTimeout("busy")):
            result = cancel_scheduled_submission({"job_id": "job1"})
        assert result["error"] == "job_busy"

    def test_cancel_non_pending_refuses(self, submit_mocks):
        with mock.patch(
            "tools.submit.get_job",
            return_value={"id": "job1", "status": "submitted", "file_ids": []},
        ):
            result = cancel_scheduled_submission({"job_id": "job1"})
        assert result["error"] == "invalid_argument"


class TestSubmitSpecsAndRecommendations:
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
