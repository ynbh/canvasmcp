from __future__ import annotations

from auth import _missing_chrome_session_error, _read_chrome_cookies, resolve_canvas_base_url

from .assignments import CanvasAssignmentsMixin
from .base import CanvasClientBase
from .content import CanvasContentMixin
from .courses import CanvasCoursesMixin


class CanvasClient(
    CanvasCoursesMixin,
    CanvasAssignmentsMixin,
    CanvasContentMixin,
    CanvasClientBase,
):
    pass


def create_canvas_client_from_env() -> CanvasClient:
    base_url = resolve_canvas_base_url()
    cookies = _read_chrome_cookies(base_url)
    if cookies:
        return CanvasClient(
            token_provider=lambda: "chrome-session-auth",
            base_url=base_url,
            cookie_provider=lambda: _read_chrome_cookies(base_url),
        )
    raise _missing_chrome_session_error(base_url)
