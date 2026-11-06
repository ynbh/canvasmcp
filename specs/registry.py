from __future__ import annotations

from jsonschema import Draft202012Validator

from auth import CanvasAPIError
from specs.assignments import ASSIGNMENT_TOOL_SPECS
from specs.content import CONTENT_TOOL_SPECS
from specs.core import CORE_TOOL_SPECS
from specs.courses import COURSE_TOOL_SPECS
from specs.inbox import INBOX_TOOL_SPECS
from specs.schema import ToolSpec
from tools.common import canvas_api_tool_error, missing_argument, tool_error

TOOL_SPECS: list[ToolSpec] = [
    *CORE_TOOL_SPECS,
    *COURSE_TOOL_SPECS,
    *ASSIGNMENT_TOOL_SPECS,
    *CONTENT_TOOL_SPECS,
    *INBOX_TOOL_SPECS,
]

_SPEC_MAP: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}

# A blank query returns no matches by design, so it skips the blank check below.
_BLANK_ALLOWED = {("resolve_course", "query")}


def _is_blank(value: object) -> bool:
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not any(str(item).strip() for item in value)
    return False


def dispatch_tool_call(
    name: str, args: dict[str, object] | None = None
) -> dict[str, object]:
    spec = _SPEC_MAP.get(name)
    if spec is None:
        return tool_error("unknown_tool", f"Unknown tool: {name}")

    payload = {
        key: value
        for key, value in (args or {}).items()
        if value is not None or key not in spec.parameters["properties"]
    }
    error = next(Draft202012Validator(spec.parameters).iter_errors(payload), None)
    if error is not None:
        path = ".".join(map(str, error.absolute_path))
        message = f"{path}: {error.message}" if path else error.message
        code = (
            "missing_argument" if error.validator == "required" else "invalid_argument"
        )
        return tool_error(code, message)

    # The schema accepts "" and [], so blank required values are rejected here.
    for key in spec.parameters.get("required", []):
        if (name, key) not in _BLANK_ALLOWED and _is_blank(payload[key]):
            return missing_argument(key)

    try:
        return spec.handler(payload)
    except CanvasAPIError as exc:
        return canvas_api_tool_error(exc)
    except Exception as exc:
        return tool_error("internal_error", str(exc))
