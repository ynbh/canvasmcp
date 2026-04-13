from __future__ import annotations

from auth import CanvasAPIError
from specs.assignments import ASSIGNMENT_TOOL_SPECS
from specs.content import CONTENT_TOOL_SPECS
from specs.core import CORE_TOOL_SPECS
from specs.courses import COURSE_TOOL_SPECS
from specs.schema import ToolHandler, ToolSpec

TOOL_SPECS: list[ToolSpec] = [
    *CORE_TOOL_SPECS,
    *COURSE_TOOL_SPECS,
    *ASSIGNMENT_TOOL_SPECS,
    *CONTENT_TOOL_SPECS,
]

_TOOL_MAP: dict[str, ToolHandler] = {spec.name: spec.handler for spec in TOOL_SPECS}


def dispatch_tool_call(name: str, args: dict[str, object] | None = None) -> dict[str, object]:
    handler = _TOOL_MAP.get(name)
    if handler is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return handler(args or {})
    except CanvasAPIError as exc:
        return {"error": str(exc)}
