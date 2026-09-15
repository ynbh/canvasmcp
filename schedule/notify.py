from __future__ import annotations

import subprocess


def _escape_applescript(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def notify(message: str, *, title: str = "Canvas") -> None:
    script = (
        f'display notification "{_escape_applescript(message)}" '
        f'with title "{_escape_applescript(title)}"'
    )
    try:
        subprocess.run(
            ["osascript", "-e", script], check=False, capture_output=True, text=True
        )
    except OSError:
        return
