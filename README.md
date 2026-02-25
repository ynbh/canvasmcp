# canvasmcp (Python + uv)

`canvasmcp` is a FastMCP server for Canvas with:
- FastMCP server exposing Canvas tools over MCP
- `uv` workflow for dependency management and running

## MCP Server Overview

The server exposes typed tools that wrap Canvas API calls.
An MCP client sends tool calls (for example `list_courses` or `canvas_get_page`) and receives structured JSON responses.
Authentication is done with your Canvas API token via environment variables.

## Prereqs

- Python 3.11+
- `uv` installed
- Canvas host:
  - `CANVAS_BASE_URL` (example: `https://school.instructure.com`)
  - If omitted, defaults to `https://canvas.instructure.com`

## Auth

Use Canvas API token auth.

Set:

```bash
export CANVAS_API_TOKEN="..."
```

Also supported: `CANVAS_API_KEY`, `canvas_api_token`, `canvas_api_key`.

Transport does not change Canvas auth. Whether you run `stdio` or HTTP, the
server process must have a Canvas token in its environment.

## Install

```bash
uv sync
```

## Environment

`.env` example:

```bash
CANVAS_BASE_URL=https://canvas.instructure.com
CANVAS_API_TOKEN=...
```

## Run MCP server (stdio)

```bash
uv run --env-file .env canvas-mcp
```

Or with the repo script (loads `.env`):

```bash
./scripts/start_mcp_server.sh
```

## Switch Transport (stdio vs HTTP)

Default transport is `stdio`.

Run as HTTP (`streamable-http`) on port `8000`:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 \
uv run --env-file .env canvas-mcp
```

Equivalent via the startup script:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 \
./scripts/start_mcp_server.sh
```

Supported `MCP_TRANSPORT` values:
- `stdio` (default)
- `http`
- `sse`
- `streamable-http`

## API Token With HTTP Transport

HTTP transport changes only how MCP clients connect to this server. Canvas auth
is still done by this server calling Canvas with your token.

Example:

```bash
CANVAS_BASE_URL="https://school.instructure.com" \
CANVAS_API_TOKEN="YOUR_CANVAS_TOKEN" \
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 \
uv run canvas-mcp
```

Using `.env` is usually cleaner for both modes:

```bash
CANVAS_BASE_URL=https://school.instructure.com
CANVAS_API_TOKEN=YOUR_CANVAS_TOKEN
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

## Supported Platforms

`canvasmcp` works with any MCP client that supports command-based (`stdio`) servers.

Verified:
- Codex CLI / Codex app MCP integration
- FastMCP CLI (`fastmcp list`, `fastmcp call`)

Usually compatible (if MCP stdio is supported by your client version):
- Claude Desktop
- Cursor
- Windsurf
- Cline-compatible MCP clients

### Codex setup

```bash
codex mcp add canvasmcp -- /absolute/path/to/canvasmcp/scripts/start_mcp_server.sh
codex mcp list
```

### Generic MCP client setup

Most clients accept a config block like this:

```json
{
  "mcpServers": {
    "canvasmcp": {
      "command": "/absolute/path/to/canvasmcp/scripts/start_mcp_server.sh"
    }
  }
}
```

## MCP Tools

Current tools exposed by `canvas-mcp`:

1. `get_today()`
2. `list_courses(favorites_only=True, search=None, limit=50)`
3. `resolve_course(query, favorites_only=True, limit=5)`
4. `list_course_assignments(course_id, search=None, bucket=None, include_submission=False, limit=100)`
5. `get_assignment_details(course_id, assignment_id, include_submission=False)`
6. `list_course_files(course_id, search=None, sort=None, order=None, limit=100)`
7. `download_course_file(course_id, file_id, force_refresh=False)`
8. `list_course_folders(course_id, limit=150)`
9. `list_modules(course_id, search=None, include_items=False, include_content_details=False, limit=100, items_limit=100)`
10. `canvas_get_page(course_id, url_or_id, force_as_id=False)`
11. `list_announcements(course_ids, start_date=None, end_date=None, active_only=True, limit=100)`
12. `list_calendar_events(course_ids=None, type=None, start_date=None, end_date=None, all_events=None, limit=100)`
13. `list_course_people(course_id, search=None, enrollment_types=None, include_email=True, limit=100)`

## File Downloads (MCP)

- `download_course_file(course_id, file_id, force_refresh?)`
- Files are saved in the system temp directory under `canvas_files_{user}`.
- Files are kept until manually removed.

## Deployment

There are two deployment modes:

1. Local sidecar (recommended for desktop MCP clients)
- Run on the same machine as your MCP client:
  - `./scripts/start_mcp_server.sh`
- This is the default and uses `stdio`.

2. Network service (for hosted setups)
- `mcp_server.py` supports non-stdio transports through env vars:
  - `MCP_TRANSPORT=streamable-http` (or `http`, `sse`)
  - `MCP_HOST=0.0.0.0`
  - `MCP_PORT=8000`
- Canvas auth still requires `CANVAS_API_TOKEN` (or alias vars) in the server environment.
- Example:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 \
uv run --env-file .env canvas-mcp
```

For production deployment, put the service behind a reverse proxy/TLS layer and restrict network access.
