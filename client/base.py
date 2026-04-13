from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
from urllib.parse import urlparse

from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from canvasapi.paginated_list import PaginatedList
from canvasapi.util import combine_kwargs

from auth import CanvasAPIError
from auth.urls import canvas_root_url, normalize_canvas_api_base_url

DEFAULT_CANVAS_BASE_URL = "https://canvas.instructure.com"
MAX_PER_PAGE = 100


@dataclass(slots=True)
class CanvasClientBase:
    token_provider: Callable[[], str]
    base_url: str = DEFAULT_CANVAS_BASE_URL
    cookie_provider: Callable[[], tuple[str, str] | None] | None = None
    _root_url: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._root_url = canvas_root_url(normalize_canvas_api_base_url(self.base_url))

    @staticmethod
    def _close_canvas(canvas: Canvas) -> None:
        requester = getattr(canvas, "_Canvas__requester", None)
        session = getattr(requester, "_session", None)
        if session is not None:
            session.close()

    def _inject_session_cookies(self, canvas: Canvas) -> None:
        if not self.cookie_provider:
            return
        cookies = self.cookie_provider()
        if not cookies:
            return
        session_cookie, csrf_token = cookies
        requester = getattr(canvas, "_Canvas__requester", None)
        if requester is None:
            return
        requester.access_token = ""
        http_session = getattr(requester, "_session", None)
        if http_session is not None:
            domain = urlparse(self._root_url).hostname or ""
            http_session.cookies.set("canvas_session", session_cookie, domain=domain)
            http_session.cookies.set("_csrf_token", csrf_token, domain=domain)
            http_session.headers.update({"X-CSRF-Token": csrf_token})

    def _run_with_canvas(self, call: Callable[[Canvas], Any]) -> Any:
        canvas = Canvas(self._root_url, self.token_provider())
        self._inject_session_cookies(canvas)
        try:
            return call(canvas)
        finally:
            self._close_canvas(canvas)

    def _call_canvas(self, action: Callable[[Canvas], Any], context: str) -> Any:
        try:
            return self._run_with_canvas(action)
        except (CanvasException, TypeError, ValueError) as exc:
            raise CanvasAPIError(
                f"Canvas request failed: {context}. Response: {exc}"
            ) from exc

    @staticmethod
    def _item_to_dict(item: Any) -> dict[str, Any]:
        if isinstance(item, dict):
            return dict(item)

        payload: dict[str, Any] = {}
        for key, value in vars(item).items():
            if key.startswith("_") or key.endswith("_date"):
                continue
            payload[key] = value
        return payload

    @staticmethod
    def _take_limit(items: Iterable[Any], limit: int) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 300))
        out: list[dict[str, Any]] = []
        for item in items:
            out.append(CanvasClientBase._item_to_dict(item))
            if len(out) >= safe_limit:
                break
        return out

    def _paginate_list(
        self, items: Iterable[Any], *, limit: int = 100
    ) -> list[dict[str, Any]]:
        return self._take_limit(items, limit)

    @staticmethod
    def _custom_paginated_call(
        canvas: Canvas,
        *,
        content_class: type[Any],
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> PaginatedList:
        requester = getattr(canvas, "_Canvas__requester")
        if params:
            return PaginatedList(
                content_class,
                requester,
                "GET",
                endpoint,
                _kwargs=combine_kwargs(**params),
            )
        return PaginatedList(content_class, requester, "GET", endpoint)
