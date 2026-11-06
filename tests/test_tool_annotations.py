from __future__ import annotations

import asyncio

from canvas_mcp.server import mcp

# Tools that change something in Canvas; everything else is read-only.
WRITE_TOOLS = {"confirm_assignment_submission", "cancel_scheduled_submission"}


def _tools():
    return asyncio.run(mcp.list_tools())


def _hints(tool):
    # Newer MCP SDKs renamed readOnlyHint/destructiveHint to snake_case and deprecate the old names.
    hints = tool.annotations
    assert hints is not None, tool.name
    if hasattr(type(hints), "read_only_hint") or "read_only_hint" in getattr(type(hints), "model_fields", {}):
        return hints.read_only_hint, hints.destructive_hint
    return hints.readOnlyHint, hints.destructiveHint


def test_only_canvas_writes_need_approval():
    tools = _tools()
    assert len(tools) > 30
    for tool in tools:
        read_only, destructive = _hints(tool)
        if tool.name in WRITE_TOOLS:
            assert read_only is False and destructive is True, tool.name
        else:
            assert read_only is True and destructive is False, tool.name


def test_open_world_hint_is_not_closed():
    for tool in _tools():
        hints = tool.annotations
        open_world = getattr(hints, "open_world_hint", None)
        if open_world is None:
            open_world = getattr(hints, "openWorldHint", None)
        assert open_world is not False, tool.name


def test_every_write_tool_exists():
    assert WRITE_TOOLS <= {tool.name for tool in _tools()}


def test_mcp_advertises_each_spec_schema_unchanged():
    from specs.registry import TOOL_SPECS

    advertised = {tool.name: tool.parameters for tool in _tools()}
    for spec in TOOL_SPECS:
        assert advertised[spec.name] == spec.parameters, spec.name


def test_mcp_call_returns_dispatch_result_as_text_and_structured():
    import json

    from fastmcp import Client

    async def call():
        async with Client(mcp) as client:
            return await client.call_tool(
                "list_course_assignments", {"course_id": "1", "bucket": "x"}, raise_on_error=False
            )

    result = asyncio.run(call())
    assert result.structured_content["error"] == "invalid_argument"
    assert json.loads(result.content[0].text) == result.structured_content
