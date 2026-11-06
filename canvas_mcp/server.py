from __future__ import annotations

import argparse
import asyncio
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool, ToolResult

from auth import ensure_canvas_auth_configured
from specs.registry import TOOL_SPECS, dispatch_tool_call
from tools.files import read_course_file

mcp = FastMCP("canvas-mcp")


class _SpecTool(Tool):
    """Advertises the spec's JSON schema as-is and runs the tool through dispatch."""

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        result = await asyncio.to_thread(dispatch_tool_call, self.name, arguments)
        return ToolResult(content=result, structured_content=result)


for spec in TOOL_SPECS:
    mcp.add_tool(
        _SpecTool(
            name=spec.name,
            description=spec.description,
            parameters=spec.parameters,
            output_schema={"type": "object", "additionalProperties": True},
            # openWorldHint stays at its default: every Canvas tool talks to a remote, multi-user system.
            annotations={"readOnlyHint": spec.read_only, "destructiveHint": not spec.read_only},
        )
    )


mcp.tool(
    read_course_file,
    name="read_course_file",
    annotations={"readOnlyHint": True, "destructiveHint": False},
    description=(
        "Return a Canvas course file inline as an MCP embedded binary resource. "
        "Use for files you want the chat model to inspect; for large files or "
        "a persistent local copy, use download_course_file."
    ),
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Canvas FastMCP server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "http", "streamable-http", "sse"),
        default="stdio",
        help="Transport to expose. FastMCP recommends http for network access.",
    )
    parser.add_argument("--host", help="Host interface for HTTP-based transports.")
    parser.add_argument("--port", type=int, help="Port for HTTP-based transports.")
    parser.add_argument(
        "--path",
        help="Custom MCP endpoint path for HTTP-based transports (default FastMCP path is /mcp for http).",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Disable the FastMCP startup banner.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    ensure_canvas_auth_configured()
    args = _build_parser().parse_args(argv)

    run_kwargs: dict[str, Any] = {"show_banner": not args.no_banner}
    if args.transport != "stdio":
        if args.host is not None:
            run_kwargs["host"] = args.host
        if args.port is not None:
            run_kwargs["port"] = args.port
        if args.path is not None:
            run_kwargs["path"] = args.path

    mcp.run(args.transport, **run_kwargs)


if __name__ == "__main__":
    main()
