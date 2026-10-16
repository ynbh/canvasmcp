from __future__ import annotations

import os
from urllib.parse import unquote, urlparse

import browser_cookie3

from .chrome_cookies import (
    cookie_query_domain,
    list_canvas_cookie_domains,
    read_chrome_cookies,
    select_canvas_session,
)
from .errors import CanvasAPIError
from .profiles import resolve_chrome_profile_path

CanvasSessionCookies = tuple[str, str]


def cookie_browser() -> str:
    browser = os.getenv("CANVAS_COOKIE_BROWSER", "chrome").strip().lower()
    if browser not in {"chrome", "firefox"}:
        raise CanvasAPIError("CANVAS_COOKIE_BROWSER must be chrome or firefox.")
    return browser


def _read_firefox_session(base_url: str | None) -> CanvasSessionCookies:
    hostname = (urlparse(base_url or "").hostname or "").lower()
    if not hostname:
        raise CanvasAPIError("Set CANVAS_BASE_URL when using Firefox cookies.")
    try:
        jar = browser_cookie3.firefox(domain_name=cookie_query_domain(hostname))
    except Exception as exc:
        raise CanvasAPIError("Could not read Firefox Canvas cookies.") from exc
    session = select_canvas_session(hostname, (c for c in jar if not c.is_expired()))
    if session:
        return session
    raise CanvasAPIError(f"Log into {base_url} in Firefox, then retry.")


def read_chrome_session_cookies(
    base_url: str | None,
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> tuple[str, str] | None:
    session_cookie = os.getenv("CANVAS_SESSION_COOKIE", "").strip()
    csrf_token = os.getenv("CANVAS_CSRF_TOKEN", "").strip()
    if session_cookie or csrf_token:
        if not (session_cookie and csrf_token):
            raise CanvasAPIError(
                "Set both CANVAS_SESSION_COOKIE and CANVAS_CSRF_TOKEN, or unset both."
            )
        return session_cookie, csrf_token
    if cookie_browser() == "firefox":
        return _read_firefox_session(base_url)
    try:
        return read_chrome_cookies(
            base_url,
            profile_path=resolve_chrome_profile_path(
                profile_name=profile_name,
                profile_path=profile_path,
            ),
        )
    except Exception:
        return None


def apply_chrome_session_to_http_session(
    http_session,
    *,
    base_url: str,
    cookies: CanvasSessionCookies,
    headers: dict[str, str] | None = None,
) -> None:
    session_cookie, csrf_token = cookies
    domain = urlparse(base_url).hostname or ""
    http_session.cookies.set("canvas_session", session_cookie, domain=domain)
    http_session.cookies.set("_csrf_token", csrf_token, domain=domain)

    request_headers = {"X-CSRF-Token": unquote(csrf_token)}
    if headers:
        request_headers.update(headers)
    http_session.headers.update(request_headers)


def list_canvas_cookie_domains_for_profile(
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> tuple[list[str], str | None]:
    try:
        domains = list_canvas_cookie_domains(
            profile_path=resolve_chrome_profile_path(
                profile_name=profile_name,
                profile_path=profile_path,
            )
        )
        return domains, None
    except Exception as exc:
        detail = str(exc).strip()
        return [], detail or "Chrome cookies could not be read."
