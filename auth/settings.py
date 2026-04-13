from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "canvasmcp"
CONFIG_PATH = CONFIG_DIR / "settings.json"


def _normalize_settings(data: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    profile_name = str(data.get("chrome_profile_name", "")).strip()
    profile_path = str(data.get("chrome_profile_path", "")).strip()
    if profile_name:
        out["chrome_profile_name"] = profile_name
    if profile_path:
        out["chrome_profile_path"] = profile_path
    return out


def load_settings() -> dict[str, str]:
    try:
        raw = json.loads(CONFIG_PATH.read_text())
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, TypeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return _normalize_settings(raw)


def save_settings(settings: dict[str, Any]) -> dict[str, str]:
    normalized = _normalize_settings(settings)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n")
    return normalized


def clear_settings() -> None:
    try:
        CONFIG_PATH.unlink()
    except FileNotFoundError:
        return


def set_selected_profile(*, name: str, path: str) -> dict[str, str]:
    return save_settings(
        {
            "chrome_profile_name": name,
            "chrome_profile_path": path,
        }
    )
