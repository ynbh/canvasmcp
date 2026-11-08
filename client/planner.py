from __future__ import annotations

from typing import Any

from canvasapi import Canvas
from canvasapi.util import combine_kwargs

from .base import MAX_PER_PAGE, _CanvasDictItem


class CanvasPlannerMixin:
    """The current user's Canvas To Do list (the planner): its items, personal to-do notes, and whether each item
    is marked done.

    Writes only ever touch the user's own planner: planner notes (POST, PUT, DELETE /planner_notes) and planner
    overrides, which hold an item's done or dismissed state (POST, PUT /planner/overrides). Nothing here submits,
    opens, or changes coursework.
    """

    def list_planner_items(
        self, *, start_date: str | None = None, end_date: str | None = None, incomplete_only: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if incomplete_only:
                params["filter"] = "incomplete_items"
            items = self._custom_paginated_call(
                canvas, content_class=_CanvasDictItem, endpoint="planner/items", params=params
            )
            return self._take_limit(items, limit=limit)

        return self._call_canvas(_load, "list planner items")

    def get_planner_note(self, *, note_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request("GET", f"planner_notes/{note_id}").json()

        return self._call_canvas(_load, f"get to-do note {note_id}")

    def create_planner_note(self, *, fields: dict[str, Any]) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request("POST", "planner_notes", _kwargs=combine_kwargs(**fields)).json()

        return self._call_canvas(_load, "create to-do note")

    def update_planner_note(self, *, note_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request("PUT", f"planner_notes/{note_id}", _kwargs=combine_kwargs(**fields)).json()

        return self._call_canvas(_load, f"update to-do note {note_id}")

    def delete_planner_note(self, *, note_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request("DELETE", f"planner_notes/{note_id}").json()

        return self._call_canvas(_load, f"delete to-do note {note_id}")

    def list_planner_overrides(self) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            overrides = self._custom_paginated_call(
                canvas, content_class=_CanvasDictItem, endpoint="planner/overrides", params={"per_page": MAX_PER_PAGE}
            )
            return self._take_limit(overrides, limit=300)

        return self._call_canvas(_load, "list planner overrides")

    def create_planner_override(
        self, *, plannable_type: str, plannable_id: str, state: dict[str, bool]
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request(
                "POST",
                "planner/overrides",
                _kwargs=combine_kwargs(plannable_type=plannable_type, plannable_id=plannable_id, **state),
            ).json()

        return self._call_canvas(_load, f"mark {plannable_type} {plannable_id}")

    def update_planner_override(self, *, override_id: str, state: dict[str, bool]) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request("PUT", f"planner/overrides/{override_id}", _kwargs=combine_kwargs(**state)).json()

        return self._call_canvas(_load, f"update planner override {override_id}")
