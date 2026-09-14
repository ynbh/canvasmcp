from __future__ import annotations

from auth import (
    missing_chrome_session_error,
    read_chrome_session_cookies,
    resolve_canvas_base_url,
)

from .assignments import CanvasAssignmentsMixin
from .base import CanvasClientBase
from .content import CanvasContentMixin
from .courses import CanvasCoursesMixin
from .submissions_write import CanvasSubmissionsWriteMixin


class CanvasClient(
    CanvasCoursesMixin,
    CanvasAssignmentsMixin,
    CanvasSubmissionsWriteMixin,
    CanvasContentMixin,
    CanvasClientBase,
):
    pass


def create_canvas_client_from_env() -> CanvasClient:
    base_url = resolve_canvas_base_url()
    cookies = read_chrome_session_cookies(base_url)
    if cookies:
        return CanvasClient(
            base_url=base_url,
            cookie_provider=lambda: read_chrome_session_cookies(base_url),
        )
    raise missing_chrome_session_error(base_url)
