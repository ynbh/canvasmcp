from unittest.mock import Mock

import pytest
from jsonschema import Draft202012Validator

from specs import registry
from specs.schema import tool_spec


@pytest.fixture
def handler(monkeypatch):
    handler = Mock(side_effect=lambda args: {"args": args})
    spec = tool_spec(
        name="example",
        handler=handler,
        description="Validation fixture",
        properties={
            "name": {"type": "string"},
            "now": {"type": "boolean"},
            "files": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer", "minimum": 1, "maximum": 10},
            "offset": {"type": "integer"},
            "status": {"type": "string", "enum": ["pending", "submitted"]},
        },
        required=["name"],
    )
    monkeypatch.setitem(registry._SPEC_MAP, "example", spec)
    return handler


@pytest.mark.parametrize(
    "args",
    [
        {"name": "demo", "now": "false"},
        {"name": "demo", "files": [None]},
        {"name": "demo", "files": [123]},
        {"name": "demo", "limit": True},
        {"name": "demo", "limit": 0},
        {"name": "demo", "limit": 11},
        {"name": "demo", "status": "unknown"},
        {"name": "demo", "unknown": None},
    ],
)
def test_invalid_arguments_never_reach_handler(handler, args):
    result = registry.dispatch_tool_call("example", args)
    assert result["error"] == "invalid_argument"
    handler.assert_not_called()


@pytest.mark.parametrize("args", [{}, {"name": None}])
def test_required_argument(handler, args):
    assert registry.dispatch_tool_call("example", args)["error"] == "missing_argument"
    handler.assert_not_called()


def test_optional_none_and_unbounded_integer(handler):
    result = registry.dispatch_tool_call(
        "example", {"name": "demo", "now": None, "offset": 1000}
    )
    assert result == {"args": {"name": "demo", "offset": 1000}}


def test_registered_schemas_are_valid():
    for spec in registry.TOOL_SPECS:
        Draft202012Validator.check_schema(spec.parameters)
