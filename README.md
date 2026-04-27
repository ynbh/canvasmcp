# canvas-cli

Local Canvas LMS access for terminal workflows, coding agents, and optional MCP clients.

Includes:

- `canvas` CLI
- optional MCP server
- Chrome-cookie auth

## Install

Preferred install:

```bash
uv tool install git+https://github.com/ynbh/canvasmcp.git
canvas --help
canvas-mcp --help
```

Pin to a branch, tag, or commit when needed:

```bash
uv tool install git+https://github.com/ynbh/canvasmcp.git@main
uv tool install git+https://github.com/ynbh/canvasmcp.git@<commit-or-tag>
```

## Development

For local development from a checkout:

```bash
uv sync
uv run canvas --help
uv run canvas-mcp --help
```

## Auth

Auth uses Chrome cookies via `browser_cookie3`.

```bash
canvas auth-status
canvas settings profiles
canvas settings choose-profile
canvas settings show
```

Set the Canvas host when auto-detection is ambiguous:

```bash
CANVAS_BASE_URL=https://school.instructure.com
```

macOS may prompt for Keychain access.

## CLI

Resolve a course:

```bash
canvas resolve "ENGL394" --all
canvas courses --all --search ENGL394
```

Inspect a course:

```bash
canvas course overview 12345
canvas course context 12345
canvas course modules 12345 --items
canvas course grades 12345
```

Assignments:

```bash
canvas assignments list 12345 --bucket upcoming
canvas assignments list 12345 --search infographic
canvas assignments show 12345 67890
canvas assignments rubric 12345 67890
```

Submissions:

```bash
canvas course submissions 12345 --student-id self
canvas course submissions 12345 --assignment 67890 --student-id self
```

Discussions:

```bash
canvas discussion list 12345
canvas discussion show 12345 67890
```

Files:

```bash
canvas files list 12345
canvas files download 12345 67890
canvas files folders 12345
```

To Do and announcements:

```bash
canvas todo
canvas todo --course 12345
canvas announcements --course 12345
```

Canvas URLs:

```bash
canvas url "https://school.instructure.com/courses/12345/assignments/67890"
```

Raw tool fallback:

```bash
canvas tool list
canvas tool run list_courses --args '{"limit":10}'
```

Use `canvas tool run` only when no first-class CLI command exists.

## Agents

Recommended setup:

1. Install the `canvas` CLI.
2. Give the agent Canvas CLI instructions/skill.
3. Let the agent call `canvas` from the terminal.

Example commands an agent should prefer:

```bash
canvas resolve "ENGL394" --all
canvas assignments list 1402756 --search infographic --limit 20
canvas assignments rubric 1402756 7543238
canvas course context 1402756
```

Example prompts:

```text
Find my ENGL394 course and summarize assignments due this week.
```

```text
Find the rubric for my infographic assignment and turn it into a checklist.
```

```text
Check whether I submitted the latest ENGL394 assignment and show the submission receipt details.
```

Agent rules:

- Resolve the course first.
- Use first-class CLI commands before raw tool calls.
- Use assignment search before fetching assignment details when the ID is unknown.
- Use rubrics for grading criteria and checklist generation.
- Use submissions for status, feedback, comments, attachments, and rubric assessments.
- Do not start, answer, or submit quizzes.

## MCP

Optional MCP config:

```json
{
  "mcpServers": {
    "canvas": {
      "command": "/absolute/path/to/canvas-cli/scripts/start_mcp_server.sh"
    }
  }
}
```

Claude Code:

```bash
claude mcp add canvas /absolute/path/to/canvas-cli/scripts/start_mcp_server.sh
```

HTTP transport:

```bash
canvas-mcp --transport http --host 127.0.0.1 --port 8000
```

Default endpoint:

```text
http://127.0.0.1:8000/mcp
```

Stdio transport:

```bash
canvas-mcp --transport stdio
```

## Tools

| Tool                                                    | Description                                      |
| ------------------------------------------------------- | ------------------------------------------------ |
| `get_today()`                                           | Today's date in ISO format                       |
| `list_courses(favorites_only, search, limit)`           | List courses                                     |
| `resolve_course(query, favorites_only, limit)`          | Fuzzy-match a course by name                     |
| `get_course_overview(course_id)`                        | Course metadata                                  |
| `get_course_syllabus(course_id, ...)`                   | Syllabus metadata and optional body              |
| `get_course_context_snapshot(course_id, ...)`           | Course overview, upcoming work, modules, grades  |
| `list_course_assignments(course_id, ...)`               | List assignments                                 |
| `get_assignment_details(course_id, assignment_id, ...)` | Assignment details                               |
| `get_assignment_rubric(course_id, assignment_id, ...)`  | Assignment rubric criteria and settings          |
| `list_assignment_groups(course_id, ...)`                | Assignment groups and optional assignments       |
| `list_course_submissions(course_id, ...)`               | Submissions for a student                        |
| `get_course_grade_summary(course_id, ...)`              | Grade summary and assignment-group breakdown     |
| `list_modules(course_id, ...)`                          | Modules and optional module items                |
| `list_discussion_topics(course_id, ...)`                | Discussions                                      |
| `get_discussion_entries(course_id, topic_id, ...)`      | Discussion entries and replies                   |
| `list_course_pages(course_id, ...)`                     | Course pages                                     |
| `canvas_get_page(course_id, url_or_id, ...)`            | One wiki page                                    |
| `list_course_tabs(course_id, ...)`                      | Course navigation tabs                           |
| `get_course_tab(course_id, tab_id, ...)`                | One navigation tab and optional target           |
| `list_course_files(course_id, ...)`                     | Files                                            |
| `download_course_file(course_id, file_id, ...)`         | Download a file                                  |
| `list_course_folders(course_id, limit)`                 | Folders                                          |
| `list_announcements(course_ids, ...)`                   | Announcements                                    |
| `list_todo_items(course_ids, limit)`                    | Current user's Canvas To Do items                |
| `list_course_people(course_id, ...)`                    | Course users                                     |
| `resolve_canvas_url(url, fetch_details)`                | Parse a Canvas URL and optionally fetch details  |

## Notes

- `canvas_get_page` only fetches wiki pages. Use `canvas url ...` for Canvas URLs whose type is unknown.
- Non-self submission queries require Canvas permissions for viewing other students.
- Quiz support should remain read-only.
