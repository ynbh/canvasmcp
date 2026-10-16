from __future__ import annotations

import os

from auth.errors import (
    CanvasAPIError,
    missing_chrome_session_error,
)
from auth.probe import get_auth_status
from auth.resolve import resolve_canvas_base_url
from auth.session import (
    apply_chrome_session_to_http_session,
    cookie_browser,
    read_chrome_session_cookies,
)


def ensure_canvas_auth_configured() -> str:
    base_url = resolve_canvas_base_url()
    if read_chrome_session_cookies(base_url):
        if os.getenv("CANVAS_SESSION_COOKIE") and os.getenv("CANVAS_CSRF_TOKEN"):
            return "cookie-env"
        return f"{cookie_browser()}-session"
    raise missing_chrome_session_error(base_url)

__all__ = [
    "apply_chrome_session_to_http_session",
    "CanvasAPIError",
    "ensure_canvas_auth_configured",
    "get_auth_status",
    "missing_chrome_session_error",
    "read_chrome_session_cookies",
    "resolve_canvas_base_url",
]
