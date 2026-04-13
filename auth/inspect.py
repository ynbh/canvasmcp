from __future__ import annotations

from typing import Any

from .chrome_cookies import (
    detect_canvas_base_url,
    list_canvas_cookie_domains,
    list_chrome_profiles,
)

from .probe import get_auth_status
from .settings import load_settings


def _profile_status(auth_status: str) -> dict[str, Any]:
    return {
        "auth_mode": None,
        "auth_verified": False,
        "auth_status": auth_status,
        "error": None,
    }


def describe_chrome_profiles() -> list[dict[str, Any]]:
    selected_path = load_settings().get("chrome_profile_path")
    profiles: list[dict[str, Any]] = []
    for profile in list_chrome_profiles():
        domains = list_canvas_cookie_domains(profile_path=profile.path)
        if len(domains) == 1:
            base_url = detect_canvas_base_url(profile_path=profile.path)
            status = get_auth_status(base_url=base_url, profile_path=profile.path)
        elif domains:
            base_url = None
            status = _profile_status("multiple_domains")
        else:
            base_url = None
            status = _profile_status("no_canvas")

        is_selected = bool(selected_path and selected_path == profile.path)
        profiles.append(
            {
                "name": profile.name,
                "path": profile.path,
                "cookie_file": profile.cookie_file,
                "detected_canvas_domains": domains,
                "resolved_canvas_base_url": base_url,
                "auth_status": status.get("auth_status"),
                "auth_verified": status.get("auth_verified"),
                "selected": is_selected,
                "active": is_selected and status.get("auth_verified", False),
            }
        )
    return profiles
