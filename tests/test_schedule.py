from __future__ import annotations

import json
import plistlib
import threading
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from typer.testing import CliRunner

from client import CanvasClient
from schedule.caffeinate import start_caffeinate, stop_caffeinate
from schedule.fire import cancel_job, fire_job
from schedule.launchd import (
    install_job,
    start_calendar_interval,
    write_plist,
)
import schedule.fire
from schedule.store import (
    InvalidJobTransition,
    JobLockTimeout,
    consume_preview,
    create_job,
    get_job,
    get_pending_job,
    job_lock,
    load_preview,
    save_preview,
    update_job,
)


@pytest.fixture
def schedule_env(tmp_path, monkeypatch):
    root = tmp_path / "scheduled-submits"
    agents = tmp_path / "LaunchAgents"
    root.mkdir()
    agents.mkdir()
    monkeypatch.setenv("CANVASMCP_SCHEDULE_DIR", str(root))
    monkeypatch.setenv("CANVASMCP_LAUNCH_AGENTS_DIR", str(agents))
    monkeypatch.setenv("CANVASMCP_CANVAS_BIN", "/tmp/fake-canvas-bin")
    return root


@pytest.fixture(autouse=True)
def mock_launchctl(monkeypatch):
    calls: list[list[str]] = []

    def fake(argv):
        calls.append(list(argv))
        return mock.Mock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("schedule.launchd._run_launchctl", fake)
    return calls


@pytest.fixture(autouse=True)
def mock_notify(monkeypatch):
    calls: list[str] = []

    def fake(message: str, *, title: str = "Canvas") -> None:
        calls.append(message)

    monkeypatch.setattr("schedule.notify.notify", fake)
    monkeypatch.setattr("schedule.fire.notify", fake)
    return calls


@pytest.fixture(autouse=True)
def mock_caffeinate_procs(monkeypatch):
    kills: list[int] = []

    def fake_popen(argv, **kwargs):
        assert argv == ["caffeinate", "-i"]
        return mock.Mock(pid=4242)

    def fake_kill(pid: int, signal: int) -> None:
        kills.append(pid)

    monkeypatch.setattr("schedule.caffeinate.subprocess.Popen", fake_popen)
    monkeypatch.setattr("schedule.caffeinate.os.kill", fake_kill)
    return kills


def _aware(offset_seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)


def _pending_job(**overrides):
    fields = {
        "course_id": "1133~1",
        "assignment_id": "1133~99",
        "assignment_name": "Essay 1",
        "submission_type": "online_upload",
        "submit_at": _aware(-10),
        "file_ids": [11, 22],
        "filenames": ["essay.pdf", "notes.txt"],
    }
    fields.update(overrides)
    return create_job(**fields)


class TestPreviewStore:
    def test_save_and_load_preview(self, schedule_env):
        saved = save_preview({"course_id": "1", "assignment_id": "2"})
        assert saved["preview_token"]
        assert load_preview(saved["preview_token"])["course_id"] == "1"

    def test_preview_expires_after_ttl(self, schedule_env, monkeypatch):
        saved = save_preview({"course_id": "1"})
        later = datetime.fromisoformat(saved["expires_at"]) + timedelta(seconds=1)
        monkeypatch.setattr("schedule.store._now", lambda: later)
        assert load_preview(saved["preview_token"]) is None
        assert not (
            schedule_env / "previews" / f"{saved['preview_token']}.json"
        ).exists()

    def test_consume_preview_deletes_token(self, schedule_env):
        saved = save_preview({"course_id": "1"})
        consumed = consume_preview(saved["preview_token"])
        assert consumed["course_id"] == "1"
        assert load_preview(saved["preview_token"]) is None

    def test_consume_preview_only_succeeds_once(self, schedule_env):
        saved = save_preview({"course_id": "1"})
        assert consume_preview(saved["preview_token"]) is not None
        assert consume_preview(saved["preview_token"]) is None

    def test_consume_preview_refuses_expired_token(self, schedule_env, monkeypatch):
        saved = save_preview({"course_id": "1"})
        later = datetime.fromisoformat(saved["expires_at"]) + timedelta(seconds=1)
        monkeypatch.setattr("schedule.store._now", lambda: later)
        assert consume_preview(saved["preview_token"]) is None
        assert list((schedule_env / "previews").iterdir()) == []

    def test_concurrent_consumes_have_one_winner(self, schedule_env):
        saved = save_preview({"course_id": "1"})
        results: list = []
        barrier = threading.Barrier(8)

        def claim():
            barrier.wait()
            results.append(consume_preview(saved["preview_token"]))

        threads = [threading.Thread(target=claim) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert sum(result is not None for result in results) == 1

    def test_preview_never_stores_cookies(self, schedule_env):
        saved = save_preview(
            {
                "course_id": "1",
                "cookies": "canvas_session=abc",
                "csrf_token": "secret",
                "file_bytes": b"nope",
            }
        )
        raw = json.loads(
            (schedule_env / "previews" / f"{saved['preview_token']}.json").read_text()
        )
        assert "cookies" not in raw
        assert "csrf_token" not in raw
        assert "file_bytes" not in raw


class TestPendingByAssignment:
    def test_returns_pending_job_for_course_and_assignment(self, schedule_env):
        first = _pending_job()
        _pending_job(assignment_id="other")
        create_job(
            course_id=first["course_id"],
            assignment_id=first["assignment_id"],
            submission_type="online_text_entry",
            submit_at=_aware(120),
            body="later",
        )
        found = get_pending_job(first["course_id"], first["assignment_id"])
        assert found is not None
        assert found["id"] == first["id"]

    def test_ignores_non_pending_jobs(self, schedule_env):
        job = _pending_job()
        update_job(job["id"], status="submitted")
        assert get_pending_job(job["course_id"], job["assignment_id"]) is None


class TestJobTransitions:
    def test_final_status_cannot_change(self, schedule_env):
        job = _pending_job()
        update_job(job["id"], status="submitted")
        with pytest.raises(InvalidJobTransition):
            update_job(job["id"], status="pending")
        with pytest.raises(InvalidJobTransition):
            update_job(job["id"], status="cancelled")
        assert get_job(job["id"])["status"] == "submitted"

    def test_unknown_status_rejected(self, schedule_env):
        job = _pending_job()
        with pytest.raises(ValueError):
            update_job(job["id"], status="armed")

    def test_non_status_fields_still_update_on_final_job(self, schedule_env):
        job = _pending_job()
        update_job(job["id"], status="cancelled")
        assert update_job(job["id"], caffeinate_pid=None)["status"] == "cancelled"

    def test_lock_is_reentrant_in_one_thread(self, schedule_env):
        job = _pending_job()
        with job_lock(job["id"]), job_lock(job["id"], timeout=0.1):
            update_job(job["id"], caffeinate_pid=1)

    def test_lock_excludes_other_threads(self, schedule_env):
        job = _pending_job()
        acquired = threading.Event()
        release = threading.Event()

        def hold():
            with job_lock(job["id"]):
                acquired.set()
                release.wait(5)

        holder = threading.Thread(target=hold)
        holder.start()
        acquired.wait(5)
        try:
            with pytest.raises(JobLockTimeout):
                with job_lock(job["id"], timeout=0.2):
                    pass
        finally:
            release.set()
            holder.join()


class TestDeleteJob:
    def test_delete_job_removes_record(self, schedule_env):
        from schedule.store import delete_job

        job = _pending_job()
        delete_job(job["id"])
        assert get_job(job["id"]) is None
        assert get_pending_job(job["course_id"], job["assignment_id"]) is None


class TestLaunchdPlist:
    def test_write_plist_uses_local_calendar_and_canvas_bin(
        self, schedule_env, tmp_path
    ):
        submit_at = datetime(2026, 9, 10, 23, 57, tzinfo=timezone(timedelta(hours=-4)))
        path = write_plist("jobA", submit_at, canvas_bin="/opt/bin/canvas")
        data = plistlib.loads(path.read_bytes())
        local = submit_at.astimezone()
        assert data["Label"] == "com.canvasmcp.submit.jobA"
        assert data["ProgramArguments"] == [
            "/opt/bin/canvas",
            "scheduled",
            "fire",
            "jobA",
        ]
        assert data["StartCalendarInterval"] == {
            "Year": local.year,
            "Month": local.month,
            "Day": local.day,
            "Hour": local.hour,
            "Minute": local.minute,
        }
        assert start_calendar_interval(submit_at) == data["StartCalendarInterval"]

    def test_install_job_bootstraps_without_real_launchctl(
        self, schedule_env, mock_launchctl
    ):
        path = install_job("jobB", _aware(300), canvas_bin="/opt/bin/canvas")
        assert path.exists()
        assert mock_launchctl
        assert mock_launchctl[0][:1] == ["bootstrap"]
        assert mock_launchctl[0][2] == str(path)

    def test_bootout_removes_plist_before_calling_launchctl(
        self, schedule_env, monkeypatch
    ):
        path = write_plist("jobD", _aware(300), canvas_bin="/opt/bin/canvas")
        seen: list[bool] = []

        def fake(argv):
            seen.append(path.exists())
            return mock.Mock(returncode=0, stdout="", stderr="")

        monkeypatch.setattr("schedule.launchd._run_launchctl", fake)
        from schedule.launchd import bootout_job

        bootout_job("jobD")
        assert seen == [False]

    def test_install_job_raises_when_bootstrap_fails(self, schedule_env, monkeypatch):
        monkeypatch.setattr(
            "schedule.launchd._run_launchctl",
            lambda argv: mock.Mock(returncode=5, stdout="", stderr="Input/output error"),
        )
        with pytest.raises(RuntimeError, match="Input/output error"):
            install_job("jobC", _aware(300), canvas_bin="/opt/bin/canvas")


class TestCaffeinateHelpers:
    def test_start_and_stop_store_pid(self, schedule_env, mock_caffeinate_procs):
        job = _pending_job()
        assert start_caffeinate(job["id"]) == 4242
        assert get_job(job["id"])["caffeinate_pid"] == 4242
        stop_caffeinate(job["id"])
        assert mock_caffeinate_procs == [4242]
        assert get_job(job["id"])["caffeinate_pid"] is None


def _client():
    return mock.create_autospec(CanvasClient, instance=True)


class TestCancelHelpers:
    def test_cancel_pending_bootout_and_stop_caffeinate(
        self, schedule_env, mock_launchctl, mock_caffeinate_procs
    ):
        job = _pending_job()
        start_caffeinate(job["id"])
        client = _client()
        with mock.patch("schedule.fire.canvas_client", return_value=client):
            cancelled = cancel_job(job["id"])
        assert cancelled["status"] == "cancelled"
        assert get_pending_job(job["course_id"], job["assignment_id"]) is None
        assert any(call[:1] == ["bootout"] for call in mock_launchctl)
        assert 4242 in mock_caffeinate_procs
        assert [c.kwargs["file_id"] for c in client.delete_user_file.call_args_list] == [
            "11",
            "22",
        ]
        assert cancelled["file_cleanup"] == [
            {"file_id": "11", "deleted": True},
            {"file_id": "22", "deleted": True},
        ]

    def test_cancel_times_out_while_job_is_locked(self, schedule_env, monkeypatch):
        job = _pending_job()
        monkeypatch.setattr(schedule.fire, "CANCEL_LOCK_TIMEOUT_SECONDS", 0.2)
        acquired = threading.Event()
        release = threading.Event()

        def hold():
            with job_lock(job["id"]):
                acquired.set()
                release.wait(5)

        holder = threading.Thread(target=hold)
        holder.start()
        acquired.wait(5)
        try:
            with pytest.raises(JobLockTimeout):
                cancel_job(job["id"])
        finally:
            release.set()
            holder.join()
        assert get_job(job["id"])["status"] == "pending"

    def test_cancel_non_pending_is_noop(self, schedule_env, mock_launchctl):
        job = _pending_job()
        update_job(job["id"], status="submitted")
        mock_launchctl.clear()
        result = cancel_job(job["id"])
        assert result["status"] == "submitted"
        assert mock_launchctl == []


class TestFireJob:
    def test_not_pending_is_noop(self, schedule_env, mock_notify):
        job = _pending_job()
        update_job(job["id"], status="submitted")
        client = mock.create_autospec(CanvasClient, instance=True)
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch(
                "schedule.fire.get_auth_status",
                return_value={"auth_verified": True},
            ),
        ):
            result = fire_job(job["id"])
        assert result["status"] == "submitted"
        client.submit_assignment.assert_not_called()
        assert mock_notify == []

    def test_missed_window_does_not_post(self, schedule_env, mock_notify):
        job = _pending_job(submit_at=_aware(-90))
        client = mock.create_autospec(CanvasClient, instance=True)
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch(
                "schedule.fire.get_auth_status",
                return_value={"auth_verified": True},
            ),
        ):
            result = fire_job(job["id"])
        assert result["status"] == "missed"
        client.submit_assignment.assert_not_called()
        assert mock_notify
        assert "Missed" in mock_notify[0]

    def test_auth_failed_does_not_post(self, schedule_env, mock_notify):
        job = _pending_job(submit_at=_aware(-5))
        client = mock.create_autospec(CanvasClient, instance=True)
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch(
                "schedule.fire.get_auth_status",
                return_value={"auth_verified": False, "error": "expired"},
            ),
        ):
            result = fire_job(job["id"])
        assert result["status"] == "auth_failed"
        assert result["error"] == "expired"
        client.submit_assignment.assert_not_called()
        assert mock_notify

    def test_happy_submit_posts_stored_file_ids(self, schedule_env, mock_notify):
        job = _pending_job(submit_at=_aware(-5))
        client = mock.create_autospec(CanvasClient, instance=True)
        client.submit_assignment.return_value = {
            "id": 9,
            "submitted_at": "2026-09-10T23:57:05-04:00",
        }
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch(
                "schedule.fire.get_auth_status",
                return_value={"auth_verified": True},
            ),
        ):
            result = fire_job(job["id"])
        assert result["status"] == "submitted"
        assert result["result"]["submitted_at"] == "2026-09-10T23:57:05-04:00"
        client.submit_assignment.assert_called_once_with(
            course_id=job["course_id"],
            assignment_id=job["assignment_id"],
            submission={
                "submission_type": "online_upload",
                "file_ids": [11, 22],
            },
        )
        assert any("Submitted" in message for message in mock_notify)

    def test_happy_text_submit(self, schedule_env):
        job = create_job(
            course_id="c1",
            assignment_id="a1",
            assignment_name="Reflection",
            submission_type="online_text_entry",
            submit_at=_aware(-5),
            body="hello",
        )
        client = mock.create_autospec(CanvasClient, instance=True)
        client.submit_assignment.return_value = {"id": 3}
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch(
                "schedule.fire.get_auth_status",
                return_value={"auth_verified": True},
            ),
        ):
            result = fire_job(job["id"])
        assert result["status"] == "submitted"
        client.submit_assignment.assert_called_once_with(
            course_id="c1",
            assignment_id="a1",
            submission={"submission_type": "online_text_entry", "body": "hello"},
        )

    def test_missing_job(self, schedule_env):
        result = fire_job("does-not-exist")
        assert result["error"] == "not_found"

    @pytest.mark.parametrize(
        ("submit_offset", "auth", "submit_error", "status", "deleted"),
        [
            (-90, {"auth_verified": True}, None, "missed", True),
            (-5, {"auth_verified": False, "error": "x"}, None, "auth_failed", True),
            (-5, {"auth_verified": True}, RuntimeError("timeout"), "failed", False),
            (-5, {"auth_verified": True}, None, "submitted", False),
        ],
    )
    def test_uploaded_files_deleted_only_when_submit_never_attempted(
        self, schedule_env, submit_offset, auth, submit_error, status, deleted
    ):
        job = _pending_job(submit_at=_aware(submit_offset))
        client = _client()
        client.submit_assignment.side_effect = submit_error
        client.submit_assignment.return_value = {"id": 1}
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch("schedule.fire.get_auth_status", return_value=auth),
        ):
            result = fire_job(job["id"])
        assert result["status"] == status
        assert result["fired_at"]
        assert client.delete_user_file.called is deleted
        assert bool(result.get("file_cleanup")) is deleted

    def test_bootout_is_the_last_step_of_finish(self, schedule_env, mock_notify):
        # Inside the launchd fire, bootout SIGTERMs this process: everything
        # else must already be done.
        job = _pending_job(submit_at=_aware(-90))
        start_caffeinate(job["id"])
        client = _client()

        def bootout(job_id):
            stored = get_job(job_id)
            assert stored["status"] == "missed"
            assert stored["caffeinate_pid"] is None
            assert stored["file_cleanup"]
            assert mock_notify

        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch("schedule.fire.bootout_job", side_effect=bootout) as booted,
        ):
            fire_job(job["id"])
        booted.assert_called_once_with(job["id"])

    def test_cancel_waits_for_inflight_fire_then_sees_outcome(
        self, schedule_env, mock_notify
    ):
        job = _pending_job(submit_at=_aware(-5))
        in_submit = threading.Event()
        finish_submit = threading.Event()
        client = _client()

        def slow_submit(**kwargs):
            in_submit.set()
            finish_submit.wait(5)
            return {"id": 9}

        client.submit_assignment.side_effect = slow_submit
        results: dict = {}
        with (
            mock.patch("schedule.fire.canvas_client", return_value=client),
            mock.patch(
                "schedule.fire.get_auth_status", return_value={"auth_verified": True}
            ),
        ):
            firer = threading.Thread(target=lambda: results.update(fire=fire_job(job["id"])))
            firer.start()
            assert in_submit.wait(5)
            canceller = threading.Thread(
                target=lambda: results.update(cancel=cancel_job(job["id"]))
            )
            canceller.start()
            canceller.join(0.3)
            assert canceller.is_alive(), "cancel must wait for the in-flight fire"
            finish_submit.set()
            firer.join(5)
            canceller.join(5)
        assert results["fire"]["status"] == "submitted"
        assert results["cancel"]["status"] == "submitted"
        client.delete_user_file.assert_not_called()


class TestScheduledCli:
    def test_scheduled_fire_invokes_fire_job(self, schedule_env):
        from cli.bootstrap import app

        runner = CliRunner()
        with mock.patch(
            "schedule.fire.fire_job",
            return_value={"id": "j1", "status": "submitted"},
        ) as fire:
            result = runner.invoke(app, ["scheduled", "fire", "j1"])
        assert result.exit_code == 0
        fire.assert_called_once_with("j1")
        assert "submitted" in result.stdout



class TestScheduledJobTools:
    def test_list_filters_by_status_and_get_finds_by_id(self, schedule_env):
        from tools.submit import get_scheduled_submission, list_scheduled_submissions

        pending = _pending_job()
        cancelled = _pending_job(assignment_id="z")
        update_job(cancelled["id"], status="cancelled")

        listed = list_scheduled_submissions({"status": "pending"})
        assert [job["id"] for job in listed["jobs"]] == [pending["id"]]
        assert get_scheduled_submission({"job_id": cancelled["id"]})["job"]["status"] == "cancelled"
        assert get_scheduled_submission({"job_id": "nope"})["error"] == "not_found"
