from __future__ import annotations

import os

from .chrome_cookies import detect_canvas_base_url
from .errors import base_url_inference_error
from .profiles import resolve_chrome_profile_path


def resolve_canvas_base_url(
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> str:
    configured = os.getenv("CANVAS_BASE_URL", "").strip()
    if configured:
        return configured
    if os.getenv("CANVAS_COOKIE_BROWSER", "chrome").strip().lower() == "firefox":
        from .errors import CanvasAPIError
        raise CanvasAPIError("Set CANVAS_BASE_URL when using Firefox cookies.")
    detected = detect_canvas_base_url(
        profile_path=resolve_chrome_profile_path(
            profile_name=profile_name,
            profile_path=profile_path,
        )
    )
    if detected:
        return detected
    raise base_url_inference_error(
        profile_name=profile_name,
        profile_path=profile_path,
    )
