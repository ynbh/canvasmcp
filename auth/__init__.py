from __future__ import annotations

from auth.errors import (
    CanvasAPIError,
    base_url_inference_error,
    missing_chrome_session_error,
)
from auth.probe import get_auth_status
from auth.profiles import resolve_chrome_profile_path, resolve_selected_chrome_profile
from auth.resolve import resolve_canvas_base_url
from auth.session import list_canvas_cookie_domains_for_profile, read_chrome_session_cookies

_missing_chrome_session_error = missing_chrome_session_error
_read_chrome_cookies = read_chrome_session_cookies
_list_canvas_cookie_domains = list_canvas_cookie_domains_for_profile
_base_url_inference_error = base_url_inference_error
_resolve_selected_chrome_profile = resolve_selected_chrome_profile
_resolve_chrome_profile_path = resolve_chrome_profile_path


def ensure_canvas_auth_configured() -> str:
    base_url = resolve_canvas_base_url()
    if _read_chrome_cookies(base_url):
        return "chrome-session"
    raise _missing_chrome_session_error(base_url)

__all__ = [
    "CanvasAPIError",
    "ensure_canvas_auth_configured",
    "get_auth_status",
    "resolve_canvas_base_url",
]
