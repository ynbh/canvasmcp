from __future__ import annotations

import copy
import json
import os
import select
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

from cli import app, bootstrap
from cli.output import _Pretty, _render


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.delenv("CANVAS_OUTPUT", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)


def invoke_result(monkeypatch, result, args, env=None):
    monkeypatch.setattr(bootstrap, "_ensure_auth", lambda: None)
    monkeypatch.setattr(bootstrap, "dispatch_tool_call", lambda *_: result)
    return CliRunner().invoke(app, args, env=env)


def test_json_preserves_payload_and_is_compact(monkeypatch):
    payload = {
        "ok": True,
        "jobs": [{"id": "demo", "error": None}],
        "warnings": ["Stay awake"],
        "extra": "é",
    }
    original = copy.deepcopy(payload)
    result = invoke_result(
        monkeypatch,
        payload,
        ["--output", "json", "assignments", "submissions", "scheduled"],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == original == payload
    assert len(result.stdout.splitlines()) == 1
    assert "\x1b" not in result.stdout
    assert result.stderr == ""


@pytest.mark.parametrize(
    "args",
    [
        ["tool", "run", "get_today", "--args", "[1]"],
        ["tool", "run", "get_today", "--args", "{"],
        ["tool", "run", "nonexistent"],
    ],
)
def test_json_tool_usage_errors(args):
    result = CliRunner().invoke(app, ["--output", "json", *args])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]
    assert result.stderr == ""


def test_semantic_refusal_and_nested_error_context(monkeypatch):
    refused = {
        "ok": False,
        "refuse_reasons": ["locked", "attempts_exhausted"],
        "message": "Preview refused",
    }
    args = [
        "assignments",
        "submissions",
        "preview",
        "1",
        "2",
        "--type",
        "online_upload",
        "--file",
        "report.pdf",
        "--now",
    ]
    result = invoke_result(monkeypatch, refused, ["--output", "json", *args])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == refused
    result = invoke_result(monkeypatch, refused, ["--output", "pretty", *args])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "PREVIEW REFUSED" in result.stderr
    assert "locked" in result.stderr and "attempts_exhausted" in result.stderr
    assert "Confirm:" not in result.stderr
    error = {
        "error": "override_required",
        "message": "Pending job exists",
        "pending_job": {"id": "old_job"},
    }
    result = invoke_result(monkeypatch, error, ["--output", "json", "courses"])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == error


def test_environment_precedence_and_no_mode_leak(monkeypatch):
    payload = {"today": "2026-09-14"}
    result = invoke_result(
        monkeypatch, payload, ["today"], env={"CANVAS_OUTPUT": "pretty"}
    )
    assert result.stdout.strip() == "2026-09-14"
    result = invoke_result(
        monkeypatch,
        payload,
        ["--output", "json", "today"],
        env={"CANVAS_OUTPUT": "pretty"},
    )
    assert json.loads(result.stdout) == payload
    result = invoke_result(monkeypatch, payload, ["today"])
    assert json.loads(result.stdout) == payload


def render(payload, tool, width=40):
    original = copy.deepcopy(payload)
    stream = StringIO()
    view = _Pretty(Console(file=stream, width=width, force_terminal=False))
    _render(view, payload, tool)
    assert payload == original
    return stream.getvalue()


def test_preview_preserves_warning_expiry_and_exact_command():
    token = "long_token_" + "a" * 55
    payload = {
        "ok": True,
        "now": False,
        "assignment_name": "Lab",
        "course_id": "1",
        "assignment_id": "2",
        "submit_at": "2026-09-15T22:50:00-04:00",
        "planned_payload": {"files": [{"path": "/tmp/a very long folder/report.pdf"}]},
        "warnings": ["Sleep before the scheduled time prevents submission."],
        "preview_token": token,
        "expires_at": "2026-09-14T12:15:00-04:00",
    }
    text = render(payload, "preview_assignment_submission")
    assert "nothing submitted" in " ".join(text.split())
    assert "-04:00" in text
    assert "Expires at:" in text
    assert "/tmp/a very long folder/report.pdf" in text
    assert f"canvas assignments submissions confirm {token}\n" in text
    assert "--override" not in text and "--caffeinate" not in text
    assert "prevents submission" in text


def test_cancel_keeps_partial_cleanup_prominent():
    payload = {
        "ok": True,
        "job": {"id": "abc", "status": "cancelled"},
        "file_cleanup": [{"file_id": "902", "error": "Forbidden"}],
    }
    text = render(payload, "cancel_scheduled_submission", width=80)
    assert text.splitlines()[0] == "CANCELLED — file cleanup incomplete"
    assert "902" in text and "Forbidden" in text
    assert "deleted" not in text


def test_pending_job_null_error_and_requested_caffeinate(monkeypatch):
    payload = {
        "ok": True,
        "now": False,
        "job": {"id": "abc", "status": "pending", "caffeinate": True, "error": None},
    }
    result = invoke_result(
        monkeypatch,
        payload,
        ["--output", "pretty", "assignments", "submissions", "confirm", "token"],
    )
    assert result.exit_code == 0
    assert "pending (not submitted)" in result.stdout
    assert "Keep-awake requested: yes" in result.stdout
    assert result.stderr == ""


def test_fallback_html_controls_and_unknown_fields():
    text = render(
        {
            "page": {
                "body": '<p>Read <a href="https://example.test">this</a></p><script>secret()</script><ul><li>First</li></ul>'
            },
            "new_field": {"zero": 0, "missing": None},
            "title": "[bold]literal[/bold]\x1b[2J",
        },
        "canvas_get_page",
    )
    assert "https://example.test" in text and "- First" in text
    assert "secret()" not in text
    assert "Zero: 0" in text and "Missing: not supplied" in text
    assert "[bold]literal[/bold]" in text
    assert "\x1b" not in text and "\\x1b" in text


def test_partial_context_and_grade_disclaimer():
    text = render(
        {
            "errors": [{"section": "grade_summary", "error": "Forbidden"}],
            "upcoming_assignments": {"count": 0, "assignments": []},
        },
        "get_course_context_snapshot",
    )
    assert text.startswith("PARTIAL RESULT") and "Forbidden" in text
    text = render(
        {
            "raw_points": {"earned": 0, "possible": 0, "percent": None},
            "grade_estimate_disclaimer": "Drop rules are not applied.",
        },
        "get_course_grade_summary",
    )
    assert "estimates" in text and "Drop rules are not applied." in " ".join(
        text.split()
    )
    assert "Percent: not supplied" in text


def test_json_profile_selection_does_not_prompt_or_save(monkeypatch):
    from cli import settings

    monkeypatch.setattr(
        settings, "describe_chrome_profiles", lambda: [{"name": "School"}]
    )
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(
        settings, "set_selected_profile", lambda **_: pytest.fail("must not save")
    )
    result = CliRunner().invoke(app, ["--output", "json", "settings", "choose-profile"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["error"] == "profile_required"
    assert "Select profile number" not in result.output


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX PTY test")
@pytest.mark.parametrize(
    "args,expect_json",
    [
        (["today"], False),
        (["--output", "json", "today"], True),
        (["tool", "run", "get_today"], True),
        (["--output", "pretty", "tool", "run", "get_today"], False),
    ],
)
def test_real_pty_mode_selection(args, expect_json):
    import pty

    master, slave = pty.openpty()
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", "from cli import main; main()", *args],
            cwd=Path(__file__).resolve().parents[1],
            stdout=slave,
            stderr=subprocess.PIPE,
        )
        process.wait(timeout=15)
        chunks = []
        # Keep the slave open until drained: macOS discards unread PTY bytes on close.
        while select.select([master], [], [], 0.2)[0]:
            chunks.append(os.read(master, 65536))
        output = b"".join(chunks).decode()
        assert process.returncode == 0, process.stderr.read().decode()
        if expect_json:
            assert "today" in json.loads(output)
            assert "\x1b" not in output
        else:
            assert output.strip().count("-") == 2 and "{" not in output
    finally:
        os.close(master)
        if slave != -1:
            os.close(slave)


def test_hidden_scheduler_uses_same_json_error_contract(monkeypatch):
    from schedule import fire

    payload = {
        "id": "job",
        "status": "failed",
        "error": "Auth expired",
        "file_ids": ["902"],
    }
    monkeypatch.setattr(fire, "fire_job", lambda _: payload)
    result = CliRunner().invoke(app, ["scheduled", "fire", "job"])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == payload
    assert result.stderr == ""


def test_profile_picker_rejects_zero_instead_of_selecting_last_profile(monkeypatch):
    import click
    import typer

    from cli.output import OutputMode, choose_profile

    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(typer, "prompt", lambda *_args, **_kwargs: "0")
    with click.Context(click.Command("choose")) as context:
        context.meta["output"] = OutputMode.pretty
        with pytest.raises(typer.Exit) as error:
            choose_profile([{"name": "School", "auth_status": "verified"}])
    assert error.value.exit_code == 1


def test_long_filename_list_is_copyable():
    filename = "a file with many words that must remain on one physical line.pdf"
    text = render(
        {
            "ok": True,
            "job": {"id": "job", "status": "pending", "filenames": [filename]},
        },
        "get_scheduled_submission",
    )
    assert filename in [line.strip() for line in text.splitlines()]
