from __future__ import annotations

from urllib.parse import urlparse

from .chrome_cookies import list_canvas_cookie_domains, read_chrome_cookies

from .profiles import resolve_chrome_profile_path

CanvasSessionCookies = tuple[str, str]


def read_chrome_session_cookies(
    base_url: str | None,
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> tuple[str, str] | None:
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

    request_headers = {"X-CSRF-Token": csrf_token}
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
