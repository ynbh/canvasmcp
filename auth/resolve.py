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
