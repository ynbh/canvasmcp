from __future__ import annotations

from typing import Any

from tools.common import invalid_argument, missing_argument, tool_error

MAX_SCHEMA_LIMIT = 300


def _validate_string(name: str, value: Any, schema: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return invalid_argument(f"{name} must be a string")
    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(str(item) for item in schema["enum"])
        return invalid_argument(f"{name} must be one of: {allowed}")
    return None


def _validate_integer(name: str, value: Any, schema: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return invalid_argument(f"{name} must be an integer")
    minimum = schema.get("minimum")
    maximum = schema.get("maximum", MAX_SCHEMA_LIMIT)
    if minimum is not None and value < minimum:
        return invalid_argument(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        return invalid_argument(f"{name} must be <= {maximum}")
    return None


def _validate_boolean(name: str, value: Any) -> dict[str, Any] | None:
    if not isinstance(value, bool):
        return invalid_argument(f"{name} must be a boolean")
    return None


def _validate_array(name: str, value: Any, schema: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(value, list):
        return invalid_argument(f"{name} must be an array")
    item_schema = schema.get("items")
    if not isinstance(item_schema, dict):
        return None
    for index, item in enumerate(value):
        if item is None:
            continue
        item_type = item_schema.get("type")
        if item_type == "string" and not isinstance(item, str):
            return invalid_argument(f"{name}[{index}] must be a string")
        if item_type == "integer" and (isinstance(item, bool) or not isinstance(item, int)):
            return invalid_argument(f"{name}[{index}] must be an integer")
        if "enum" in item_schema and item not in item_schema["enum"]:
            allowed = ", ".join(str(entry) for entry in item_schema["enum"])
            return invalid_argument(
                f"{name}[{index}] must be one of: {allowed}"
            )
    return None


def _validate_value(
    name: str, value: Any, schema: dict[str, Any]
) -> dict[str, Any] | None:
    type_name = schema.get("type")
    if type_name == "string":
        return _validate_string(name, value, schema)
    if type_name == "integer":
        return _validate_integer(name, value, schema)
    if type_name == "boolean":
        return _validate_boolean(name, value)
    if type_name == "array":
        return _validate_array(name, value, schema)
    return None


def validate_tool_args(
    parameters: dict[str, Any], args: dict[str, object]
) -> dict[str, object] | None:
    properties = parameters.get("properties", {})
    if not isinstance(properties, dict):
        return None

    required = parameters.get("required", [])
    if not isinstance(required, list):
        required = []

    for name in required:
        if name not in args or args[name] is None:
            return missing_argument(name)
        schema = properties.get(name, {})
        if (
            isinstance(schema, dict)
            and schema.get("type") == "string"
            and not str(args[name]).strip()
        ):
            return missing_argument(name)

    for name, value in args.items():
        if value is None:
            continue
        schema = properties.get(name)
        if not isinstance(schema, dict):
            return tool_error("invalid_argument", f"Unknown argument: {name}")
        error = _validate_value(name, value, schema)
        if error is not None:
            return error
    return None
