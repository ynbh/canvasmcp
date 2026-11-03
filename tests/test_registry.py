from dataclasses import replace
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



# Pinned so that dropping a tool's `required` entry is a visible, reviewed change:
# without it, the tool would run and call Canvas with empty IDs.
REQUIRED_ARGUMENTS = {
    "get_today": [],
    "list_courses": [],
    "resolve_course": ["query"],
    "get_course_overview": ["course_id"],
    "get_course_syllabus": ["course_id"],
    "list_course_pages": ["course_id"],
    "canvas_get_page": ["course_id", "url_or_id"],
    "list_course_tabs": ["course_id"],
    "get_course_tab": ["course_id", "tab_id"],
    "list_course_people": ["course_id"],
    "list_modules": ["course_id"],
    "get_course_grade_summary": ["course_id"],
    "resolve_canvas_url": ["url"],
    "get_course_context_snapshot": ["course_id"],
    "list_course_assignments": ["course_id"],
    "get_assignment_details": ["assignment_id", "course_id"],
    "get_assignment_rubric": ["assignment_id", "course_id"],
    "list_assignment_groups": ["course_id"],
    "list_course_submissions": ["course_id"],
    "install_assignment_submission_files": ["assignment_id", "course_id"],
    "preview_assignment_submission": ["assignment_id", "course_id", "submission_type"],
    "confirm_assignment_submission": ["preview_token"],
    "list_scheduled_submissions": [],
    "get_scheduled_submission": ["job_id"],
    "cancel_scheduled_submission": ["job_id"],
    "list_discussion_topics": ["course_id"],
    "get_discussion_entries": ["course_id", "topic_id"],
    "list_course_files": ["course_id"],
    "download_course_file": ["course_id", "file_id"],
    "list_course_folders": ["course_id"],
    "list_announcements": ["course_ids"],
    "list_todo_items": [],
    "list_inbox_conversations": [],
    "get_inbox_conversation": ["conversation_id"],
}


def test_required_arguments_are_pinned():
    declared = {
        spec.name: sorted(spec.parameters.get("required", [])) for spec in registry.TOOL_SPECS
    }
    assert declared == REQUIRED_ARGUMENTS


def _valid_value(schema):
    if "enum" in schema:
        return schema["enum"][0]
    return ["1"] if schema.get("type") == "array" else "1"


@pytest.mark.parametrize(
    ("name", "required"),
    [(name, required) for name, required in REQUIRED_ARGUMENTS.items() if required],
)
def test_schema_rejects_each_missing_required_argument(monkeypatch, name, required):
    # Replace the handler so only schema validation can produce the error.
    handler = Mock()
    monkeypatch.setitem(
        registry._SPEC_MAP, name, replace(registry._SPEC_MAP[name], handler=handler)
    )
    properties = registry._SPEC_MAP[name].parameters["properties"]
    for missing in required:
        args = {arg: _valid_value(properties[arg]) for arg in required if arg != missing}
        result = registry.dispatch_tool_call(name, args)
        assert result["error"] == "missing_argument", (missing, result)
        assert missing in result["message"]
    handler.assert_not_called()
