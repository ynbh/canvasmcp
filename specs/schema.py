from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler


def tool_spec(
    *,
    name: str,
    description: str,
    handler: ToolHandler,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> ToolSpec:
    parameters: dict[str, Any] = {"type": "object", "properties": properties or {}}
    if required:
        parameters["required"] = required
    return ToolSpec(
        name=name,
        description=description,
        parameters=parameters,
        handler=handler,
    )
