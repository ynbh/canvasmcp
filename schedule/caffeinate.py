from __future__ import annotations

import os
import signal
import subprocess

from schedule.store import get_job, update_job


def _popen(argv: list[str]) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _kill(pid: int) -> None:
    os.kill(pid, signal.SIGTERM)


def start_caffeinate(job_id: str) -> int:
    proc = _popen(["caffeinate", "-i"])
    pid = int(proc.pid)
    update_job(job_id, caffeinate=True, caffeinate_pid=pid)
    return pid


def stop_caffeinate(job_id: str) -> None:
    job = get_job(job_id)
    if job is None:
        return
    pid = job.get("caffeinate_pid")
    if pid is None or pid == "":
        return
    try:
        _kill(int(pid))
    except (ProcessLookupError, PermissionError, OSError, TypeError, ValueError):
        pass
    if get_job(job_id) is not None:
        update_job(job_id, caffeinate_pid=None)
