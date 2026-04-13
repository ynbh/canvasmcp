from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import requests

from .chrome_cookies import read_chrome_cookies
from .errors import CanvasAPIError, missing_chrome_session_error
from .profiles import resolve_chrome_profile_path, resolve_selected_chrome_profile
from .resolve import resolve_canvas_base_url
from .session import list_canvas_cookie_domains_for_profile
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
    cookies = read_chrome_cookies(
        resolved_base_url,
        profile_path=resolved_profile_path,
    )
    domains, _ = list_canvas_cookie_domains_for_profile(
        profile_name=profile_name,
        profile_path=profile_path,
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
        domain = urlparse(resolved_base_url).hostname or ""
        session.cookies.set("canvas_session", session_cookie, domain=domain)
        session.cookies.set("_csrf_token", csrf_token, domain=domain)
        session.headers.update(
            {
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "canvasmcp-auth-probe",
                "X-CSRF-Token": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": root_url,
            }
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
        status["auth_mode"] = "chrome-session"
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


def ensure_canvas_auth_configured() -> str:
    status = get_auth_status()
    if status["auth_verified"]:
        return "chrome-session"
    raise CanvasAPIError(status["error"] or "Canvas auth could not be verified.")
