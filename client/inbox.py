from __future__ import annotations

from typing import Any

from canvasapi import Canvas
from canvasapi.util import combine_kwargs

from .base import MAX_PER_PAGE
from .content import _CanvasDictItem


class CanvasInboxMixin:
    """Read-only access to the current user's Canvas Inbox (conversations).

    Nothing here changes Canvas state. Fetching a single conversation marks it as
    read by default, so get_conversation always sends auto_mark_as_read=false.
    """

    def list_conversations(
        self,
        *,
        scope: str | None = None,
        course_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if scope:
                params["scope"] = scope
            if course_id:
                params["filter"] = [f"course_{course_id}"]
            conversations = self._custom_paginated_call(
                canvas,
                content_class=_CanvasDictItem,
                endpoint="conversations",
                params=params,
            )
            return self._paginate_list(conversations, limit=limit)

        return self._call_canvas(_load, "list inbox conversations")

    def get_conversation(self, *, conversation_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            response = requester.request(
                "GET",
                f"conversations/{conversation_id}",
                _kwargs=combine_kwargs(auto_mark_as_read="false"),
            )
            return response.json()

        return self._call_canvas(_load, f"get inbox conversation {conversation_id}")
