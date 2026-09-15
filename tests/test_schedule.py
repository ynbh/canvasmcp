from __future__ import annotations

import json
import plistlib
from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from typer.testing import CliRunner

from schedule.caffeinate import start_caffeinate, stop_caffeinate
from schedule.fire import cancel_job, fire_job
from schedule.launchd import (
    install_job,
    plist_label,
    start_calendar_interval,
    write_plist,
)
from schedule.store import (
    consume_preview,
    create_job,
    get_job,
    get_pending_job,
    list_jobs,
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


class TestCaffeinateHelpers:
    def test_start_and_stop_store_pid(self, schedule_env, mock_caffeinate_procs):
        job = _pending_job()
        assert start_caffeinate(job["id"]) == 4242
        assert get_job(job["id"])["caffeinate_pid"] == 4242
        stop_caffeinate(job["id"])
        assert mock_caffeinate_procs == [4242]
        assert get_job(job["id"])["caffeinate_pid"] is None


class TestCancelHelpers:
    def test_cancel_pending_bootout_and_stop_caffeinate(
        self, schedule_env, mock_launchctl, mock_caffeinate_procs
    ):
        job = _pending_job()
        start_caffeinate(job["id"])
        cancelled = cancel_job(job["id"])
        assert cancelled["status"] == "cancelled"
        assert get_pending_job(job["course_id"], job["assignment_id"]) is None
        assert any(call[:1] == ["bootout"] for call in mock_launchctl)
        assert 4242 in mock_caffeinate_procs

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
        client = mock.MagicMock()
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
        client = mock.MagicMock()
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
        client = mock.MagicMock()
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
        client = mock.MagicMock()
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
        client = mock.MagicMock()
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


class TestListJobs:
    def test_status_filter(self, schedule_env):
        pending = _pending_job()
        other = _pending_job(assignment_id="z")
        update_job(other["id"], status="cancelled")
        assert [job["id"] for job in list_jobs(status="pending")] == [pending["id"]]
        assert plist_label(pending["id"]) == f"com.canvasmcp.submit.{pending['id']}"
