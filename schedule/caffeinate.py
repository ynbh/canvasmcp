from __future__ import annotations

import os
import signal
import subprocess

from schedule.store import get_job, update_job


def start_caffeinate(job_id: str) -> int:
    proc = subprocess.Popen(
        ["caffeinate", "-i"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    pid = proc.pid
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
        os.kill(int(pid), signal.SIGTERM)
    except (OSError, TypeError, ValueError):
        pass
    if get_job(job_id) is not None:
        update_job(job_id, caffeinate_pid=None)
