from __future__ import annotations

from auth import CanvasAPIError
from specs.assignments import ASSIGNMENT_TOOL_SPECS
from specs.content import CONTENT_TOOL_SPECS
from specs.core import CORE_TOOL_SPECS
from specs.courses import COURSE_TOOL_SPECS
from specs.schema import ToolHandler, ToolSpec
from specs.validate import validate_tool_args
from tools.common import canvas_api_tool_error, tool_error

TOOL_SPECS: list[ToolSpec] = [
    *CORE_TOOL_SPECS,
    *COURSE_TOOL_SPECS,
    *ASSIGNMENT_TOOL_SPECS,
    *CONTENT_TOOL_SPECS,
]

_TOOL_MAP: dict[str, ToolHandler] = {spec.name: spec.handler for spec in TOOL_SPECS}
_SPEC_MAP: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}


def dispatch_tool_call(name: str, args: dict[str, object] | None = None) -> dict[str, object]:
    spec = _SPEC_MAP.get(name)
    if spec is None:
        return tool_error("unknown_tool", f"Unknown tool: {name}")

    payload = args or {}
    validation_error = validate_tool_args(spec.parameters, payload)
    if validation_error is not None:
        return validation_error

    try:
        return spec.handler(payload)
    except CanvasAPIError as exc:
        return canvas_api_tool_error(exc)
    except Exception as exc:
        return tool_error("internal_error", str(exc))
