from __future__ import annotations

import os
from typing import Any

import requests

from .errors import CanvasAPIError, missing_chrome_session_error
from .profiles import resolve_chrome_profile_path, resolve_selected_chrome_profile
from .chrome_cookies import (
    detect_canvas_base_url,
    list_canvas_cookie_domains,
    list_chrome_profiles,
)
from .session import (
    apply_chrome_session_to_http_session,
    cookie_browser,
    list_canvas_cookie_domains_for_profile,
    read_chrome_session_cookies,
    resolve_canvas_base_url,
)
from .settings import load_settings
from .urls import canvas_root_url, normalize_canvas_api_base_url


def get_auth_status(
    *,
    base_url: str | None = None,
    probe_path: str = "/api/v1/users/self",
    timeout_seconds: int = 20,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> dict[str, Any]:
    resolved_base_url = base_url or resolve_canvas_base_url(
        profile_name=profile_name,
        profile_path=profile_path,
    )
    selected_name, selected_profile_path = resolve_selected_chrome_profile()
    resolved_profile_path = resolve_chrome_profile_path(
        profile_name=profile_name,
        profile_path=profile_path,
    )
    root_url = canvas_root_url(normalize_canvas_api_base_url(resolved_base_url))
    cookie_env_mode = bool(
        os.getenv("CANVAS_SESSION_COOKIE") or os.getenv("CANVAS_CSRF_TOKEN")
    )
    cookie_error = None
    try:
        cookies = read_chrome_session_cookies(
            resolved_base_url,
            profile_name=profile_name,
            profile_path=profile_path or resolved_profile_path,
        )
    except CanvasAPIError as exc:
        cookies = None
        cookie_error = str(exc)
    domains, _ = (
        ([], None)
        if cookie_env_mode or cookie_error or cookie_browser() == "firefox"
        else list_canvas_cookie_domains_for_profile(
            profile_name=profile_name,
            profile_path=profile_path,
        )
    )

    status: dict[str, Any] = {
        "auth_mode": None,
        "auth_verified": False,
        "auth_status": "no_cookies",
        "configured_canvas_base_url": os.getenv("CANVAS_BASE_URL", "").strip() or None,
        "resolved_canvas_base_url": resolved_base_url,
        "selected_chrome_profile": selected_name,
        "selected_chrome_profile_path": selected_profile_path,
        "resolved_chrome_profile_path": resolved_profile_path,
        "detected_canvas_domains": domains,
        "probe_url": f"{root_url}{probe_path}",
        "probe_status": None,
        "probe_content_type": None,
        "probe_location": None,
        "error": None,
    }
    if cookie_error:
        status["error"] = cookie_error
        return status
    if not cookies:
        status["error"] = missing_chrome_session_error(
            resolved_base_url,
            profile_name=profile_name,
            profile_path=profile_path,
        ).args[0]
        return status

    session_cookie, csrf_token = cookies
    session = requests.Session()
    try:
        apply_chrome_session_to_http_session(
            session,
            base_url=resolved_base_url,
            cookies=(session_cookie, csrf_token),
            headers={
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "canvasmcp-auth-probe",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": root_url,
            },
        )
        response = session.get(
            status["probe_url"],
            allow_redirects=False,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        status["auth_status"] = "probe_failed"
        status["error"] = f"Canvas auth probe failed: {exc}"
        return status
    finally:
        session.close()

    content_type = response.headers.get("content-type", "")
    status["probe_status"] = response.status_code
    status["probe_content_type"] = content_type
    status["probe_location"] = response.headers.get("location")

    if response.status_code == 200 and "application/json" in content_type.casefold():
        status["auth_mode"] = "cookie-env" if cookie_env_mode else f"{cookie_browser()}-session"
        status["auth_verified"] = True
        status["auth_status"] = "verified"
        return status

    body_prefix = response.text[:300].casefold()
    if response.is_redirect or response.status_code in {401, 403}:
        status["auth_status"] = "not_logged_in"
    elif "central authentication service" in body_prefix or "shibboleth" in body_prefix:
        status["auth_status"] = "not_logged_in"
    else:
        status["auth_status"] = "unexpected_response"

    status["error"] = (
        f"Canvas auth probe to {probe_path} returned "
        f"{response.status_code} ({content_type or 'unknown content type'})."
    )
    return status


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
