from __future__ import annotations

import os

from .chrome_cookies import resolve_chrome_profile
from .settings import load_settings


def resolve_selected_chrome_profile() -> tuple[str | None, str | None]:
    profile_name = os.getenv("CANVAS_CHROME_PROFILE", "").strip() or None
    profile_path = os.getenv("CANVAS_CHROME_PROFILE_PATH", "").strip() or None
    if profile_name or profile_path:
        return profile_name, profile_path

    settings = load_settings()
    return (
        settings.get("chrome_profile_name") or None,
        settings.get("chrome_profile_path") or None,
    )


def resolve_chrome_profile_path(
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> str | None:
    selected_name, selected_path = resolve_selected_chrome_profile()
    resolved = resolve_chrome_profile(
        profile_name=profile_name or selected_name,
        profile_path=profile_path or selected_path,
    )
    if resolved is None:
        return profile_path or selected_path
    return resolved.path
