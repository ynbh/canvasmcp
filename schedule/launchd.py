from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from schedule.store import parse_submit_at


def plist_label(job_id: str) -> str:
    return f"com.canvasmcp.submit.{job_id}"


def launch_agents_dir() -> Path:
    override = os.environ.get("CANVASMCP_LAUNCH_AGENTS_DIR", "").strip()
    if override:
        path = Path(override).expanduser()
    else:
        path = Path.home() / "Library" / "LaunchAgents"
    path.mkdir(parents=True, exist_ok=True)
    return path


def plist_path(job_id: str) -> Path:
    return launch_agents_dir() / f"{plist_label(job_id)}.plist"


def resolve_canvas_bin() -> str:
    override = os.environ.get("CANVASMCP_CANVAS_BIN", "").strip()
    if override:
        return str(Path(override).expanduser().resolve())
    found = shutil.which("canvas")
    if found:
        return str(Path(found).resolve())
    argv0 = Path(sys.argv[0]).resolve()
    if argv0.name in {"canvas", "canvas.exe"}:
        return str(argv0)
    raise FileNotFoundError("canvas executable not found on PATH")


def start_calendar_interval(submit_at: str | datetime) -> dict[str, int]:
    parsed = parse_submit_at(submit_at)
    local = parsed.astimezone()
    return {
        "Year": local.year,
        "Month": local.month,
        "Day": local.day,
        "Hour": local.hour,
        "Minute": local.minute,
    }


def _run_launchctl(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["launchctl", *argv],
        check=False,
        capture_output=True,
        text=True,
    )


def write_plist(
    job_id: str,
    submit_at: str | datetime,
    *,
    canvas_bin: str | None = None,
) -> Path:
    binary = canvas_bin or resolve_canvas_bin()
    path = plist_path(job_id)
    payload = {
        "Label": plist_label(job_id),
        "ProgramArguments": [binary, "scheduled", "fire", job_id],
        "StartCalendarInterval": start_calendar_interval(submit_at),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        plistlib.dump(payload, handle)
    return path


def bootstrap_job(job_id: str) -> subprocess.CompletedProcess[str]:
    domain = f"gui/{os.getuid()}"
    return _run_launchctl(["bootstrap", domain, str(plist_path(job_id))])


def bootout_job(job_id: str) -> None:
    domain = f"gui/{os.getuid()}"
    try:
        _run_launchctl(["bootout", f"{domain}/{plist_label(job_id)}"])
    except OSError:
        pass
    try:
        plist_path(job_id).unlink(missing_ok=True)
    except OSError:
        pass


def install_job(
    job_id: str,
    submit_at: str | datetime,
    *,
    canvas_bin: str | None = None,
) -> Path:
    path = write_plist(job_id, submit_at, canvas_bin=canvas_bin)
    bootstrap_job(job_id)
    return path
