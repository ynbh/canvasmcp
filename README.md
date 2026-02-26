# canvasmcp

FastMCP server that exposes Canvas LMS tools over MCP.

## Setup

```bash
uv sync
```

## Auth

### Option 1: API Token

```bash
CANVAS_API_TOKEN=your_token_here
```

Also accepts: `CANVAS_API_KEY`, `canvas_api_token`, `canvas_api_key`.

### Option 2: Browser Session Cookies

Use this when you don't have an API token. Grab `canvas_session` and `_csrf_token` from your browser's cookies (DevTools → Application → Cookies).

```bash
CANVAS_AUTH_MODE=session
CANVAS_SESSION_COOKIE=your_canvas_session_cookie
CANVAS_CSRF_TOKEN=your_csrf_token
```

> **Note:** Session cookies expire when you log out or the session times out. You'll need to re-grab them when that happens.

### Base URL

```bash
CANVAS_BASE_URL=https://school.instructure.com
```

Defaults to `https://canvas.instructure.com` if omitted.

## `.env` Example

```bash
CANVAS_BASE_URL=https://school.instructure.com

# API token auth
CANVAS_API_TOKEN=your_token

# OR session cookie auth
# CANVAS_AUTH_MODE=session
# CANVAS_SESSION_COOKIE=...
# CANVAS_CSRF_TOKEN=...
```

## Run

```bash
uv run --env-file .env canvas-mcp
```

Or:

```bash
./scripts/start_mcp_server.sh
```

### HTTP Transport

Default is `stdio`. To run as HTTP:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=8000 \
uv run --env-file .env canvas-mcp
```

Supported transports: `stdio`, `http`, `sse`, `streamable-http`.

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

## Tools

| Tool                                                   | Description                                      |
| ------------------------------------------------------ | ------------------------------------------------ |
| `get_today()`                                          | Today's date in ISO format                       |
| `list_courses(favorites_only, search, limit)`          | List courses                                     |
| `resolve_course(query, favorites_only, limit)`         | Fuzzy-match a course by name                     |
| `get_course_overview(course_id)`                       | Course-level metadata and teacher info           |
| `get_course_syllabus(course_id, ...)`                  | Syllabus metadata and optional syllabus body     |
| `list_course_assignments(course_id, ...)`              | List assignments                                 |
| `get_assignment_details(course_id, assignment_id, ...)` | Full assignment details                          |
| `list_course_pages(course_id, ...)`                    | List course pages                                |
| `canvas_get_page(course_id, url_or_id, ...)`           | Get a specific wiki page (pages URLs only)       |
| `list_discussion_topics(course_id, ...)`               | List discussions with exact-title/search filters |
| `get_discussion_entries(course_id, topic_id, ...)`     | Get discussion thread entries and replies        |
| `list_course_files(course_id, ...)`                    | List files                                       |
| `download_course_file(course_id, file_id, ...)`        | Download a file to local temp storage            |
| `list_course_folders(course_id, limit)`                | List folders                                     |
| `list_assignment_groups(course_id, ...)`               | List grading groups and optional assignments     |
| `list_course_submissions(course_id, ...)`              | List submissions for a student                   |
| `get_course_grade_summary(course_id, ...)`             | Grade summary + assignment-group breakdown       |
| `list_modules(course_id, ...)`                         | List modules with optional items                 |
| `list_announcements(course_ids, ...)`                  | List announcements                               |
| `list_calendar_events(course_ids, ...)`                | List calendar events                             |
| `list_course_people(course_id, ...)`                   | List users in a course                           |
| `resolve_canvas_url(url, fetch_details)`               | Parse Canvas URL and optionally fetch details    |
| `get_course_context_snapshot(course_id, ...)`          | Aggregated course context for quick orientation  |

`canvas_get_page` does not fetch assignment submission preview routes. Use `resolve_canvas_url` for routing those URLs to the right tool.

For `list_course_submissions` with `student_id` other than `self`, Canvas must grant your token/role permission to read other students' submissions in that course.
