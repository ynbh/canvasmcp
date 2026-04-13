# canvasmcp

FastMCP server that exposes Canvas LMS tools over MCP.

## Setup

```bash
uv sync
```

## Auth

The installed CLI command is `canvas`.

Auth is Chrome-only:

- The CLI reads Canvas cookies from Chrome via `browser_cookie3`.
- If `CANVAS_BASE_URL` is set, that domain is used.
- If `CANVAS_BASE_URL` is unset, the CLI tries to auto-detect a single Canvas domain from Chrome cookies.
- Chrome cookies are read fresh on every request, so session and CSRF rotation are picked up automatically.
- Normal CLI commands run a local precheck only (base URL + cookie presence).
- `canvas auth-status` runs a live Canvas probe and returns JSON even on errors.

> **Note:** macOS will prompt for Keychain access on first run. Click "Allow" or "Always Allow".

### Base URL

```bash
CANVAS_BASE_URL=https://school.instructure.com
```

If omitted, the CLI attempts to infer the Canvas domain from Chrome cookies. Set it explicitly if you have multiple Canvas domains in Chrome.

## CLI

List your courses:

```bash
uv run canvas courses
```

Inspect one course:

```bash
uv run canvas course overview 12345
uv run canvas course context 12345
```

Work with assignments and discussions:

```bash
uv run canvas assignments list 12345 --bucket upcoming
uv run canvas discussion show 12345 67890
```

Use the raw tool escape hatch when needed:

```bash
uv run canvas tool list
uv run canvas tool run list_courses --args '{"limit":10}'
```

Check current auth status:

```bash
uv run canvas auth-status
```

Manage Chrome profile selection:

```bash
uv run canvas settings profiles
uv run canvas settings choose-profile
uv run canvas settings choose-profile "terpmail.umd.edu"
uv run canvas settings show
uv run canvas settings clear
```

## Install

Install the CLI as a tool:

```bash
uv tool install .
```

That installs the `canvas` command.

Reinstall after local changes:

```bash
uv tool install . --reinstall
```

## MCP Client Setup

```json
{
  "mcpServers": {
    "canvasmcp": {
      "command": "/absolute/path/to/canvasmcp/scripts/start_mcp_server.sh"
    }
  }
}
```

## Run As An HTTP Server

FastMCP v3 recommends HTTP transport for networked MCP servers. This project now supports that directly from the existing entrypoint:

```bash
uv run canvas-mcp --transport http --host 127.0.0.1 --port 8000
```

By default, FastMCP serves the MCP endpoint at `http://127.0.0.1:8000/mcp`.

You can also use the helper script:

```bash
./scripts/start_mcp_server.sh --transport http --host 127.0.0.1 --port 8000
```

`stdio` remains the default transport for desktop MCP clients. `sse` is still available for legacy clients:

```bash
uv run canvas-mcp --transport sse --host 127.0.0.1 --port 8000
```

## Tools

| Tool                                                    | Description                                      |
| ------------------------------------------------------- | ------------------------------------------------ |
| `get_today()`                                           | Today's date in ISO format                       |
| `list_courses(favorites_only, search, limit)`           | List courses                                     |
| `resolve_course(query, favorites_only, limit)`          | Fuzzy-match a course by name                     |
| `get_course_overview(course_id)`                        | Course-level metadata and teacher info           |
| `get_course_syllabus(course_id, ...)`                   | Syllabus metadata and optional syllabus body     |
| `list_course_assignments(course_id, ...)`               | List assignments                                 |
| `get_assignment_details(course_id, assignment_id, ...)` | Full assignment details                          |
| `list_course_pages(course_id, ...)`                     | List course pages                                |
| `list_course_tabs(course_id, ...)`                      | List left-sidebar course navigation tabs         |
| `get_course_tab(course_id, tab_id, ...)`                | Get one tab and resolve/fetch its target         |
| `canvas_get_page(course_id, url_or_id, ...)`            | Get a specific wiki page (pages URLs only)       |
| `list_discussion_topics(course_id, ...)`                | List discussions with exact-title/search filters |
| `get_discussion_entries(course_id, topic_id, ...)`      | Get discussion thread entries and replies        |
| `list_course_files(course_id, ...)`                     | List files                                       |
| `download_course_file(course_id, file_id, ...)`         | Download a file to local temp storage            |
| `list_course_folders(course_id, limit)`                 | List folders                                     |
| `list_assignment_groups(course_id, ...)`                | List grading groups and optional assignments     |
| `list_course_submissions(course_id, ...)`               | List submissions for a student                   |
| `get_course_grade_summary(course_id, ...)`              | Grade summary + assignment-group breakdown       |
| `list_modules(course_id, ...)`                          | List modules with optional items                 |
| `list_announcements(course_ids, ...)`                   | List announcements                               |
| `list_calendar_events(course_ids, ...)`                 | List calendar events                             |
| `list_course_people(course_id, ...)`                    | List users in a course                           |
| `resolve_canvas_url(url, fetch_details)`                | Parse Canvas URL and optionally fetch details    |
| `get_course_context_snapshot(course_id, ...)`           | Aggregated course context for quick orientation  |

### Navigation tabs

Use course tabs when you need the left-sidebar entries (Home, Syllabus, People, external tools, etc.) instead of only wiki pages:

- `list_course_tabs(course_id)` to enumerate available tabs and their URLs.
- `get_course_tab(course_id, tab_id, include_target=true)` to fetch one tab and resolve its destination.

`canvas_get_page` does not fetch assignment submission preview routes. Use `resolve_canvas_url` for routing those URLs to the right tool.

For `list_course_submissions` with `student_id` other than `self`, your Canvas account must have permission to read other students' submissions in that course.
