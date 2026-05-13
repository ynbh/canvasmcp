# canvas-cli

Local Canvas LMS access for terminal workflows, coding agents, and optional MCP clients.

Use the `canvas` CLI first. It is the most stable interface for local use, scripts, and coding agents. The MCP server is available when a client specifically needs MCP tool calls.

This package provides:

- `canvas`: a CLI for reading Canvas courses, assignments, submissions, files, pages, discussions, grades, announcements, and To Do items
- `canvas-mcp`: an optional MCP server exposing the same tools
- Chrome-cookie authentication via `browser_cookie3`

## Install

Install from GitHub:

```bash
uv tool install git+https://github.com/ynbh/canvasmcp.git
```

Check that the commands are available:

```bash
canvas --help
canvas-mcp --help
```

If you want a specific branch, tag, or commit:

```bash
uv tool install git+https://github.com/ynbh/canvasmcp.git@main
uv tool install git+https://github.com/ynbh/canvasmcp.git@<tag-or-commit>
```

For local development:

```bash
uv sync
uv run canvas --help
uv run canvas-mcp --help
```

## Authentication

The CLI reads your existing Canvas browser session from Chrome cookies. Open Canvas in Chrome first, then run:

```bash
canvas auth-status
```

If authentication fails or points at the wrong account, inspect and select the Chrome profile explicitly:

```bash
canvas settings profiles
canvas settings choose-profile
canvas settings show
```

What to check:

- `canvas auth-status`: verifies whether Canvas cookies can be read and whether the configured Canvas host works.
- `canvas settings profiles`: lists Chrome profiles and whether each one appears to contain Canvas cookies.
- `canvas settings choose-profile`: saves the Chrome profile the CLI should use.
- `canvas settings show`: shows the selected profile and current auth-related settings.
- `canvas settings clear`: removes saved profile settings if you want to start over.

Common fixes:

- Log in to Canvas in Chrome, then rerun `canvas auth-status`.
- If you use multiple Chrome profiles, run `canvas settings profiles`, then `canvas settings choose-profile "<profile name>"`.
- If the CLI detects the wrong Canvas host, set `CANVAS_BASE_URL`.
- If the saved profile is stale, run `canvas settings clear`, then choose the profile again.
- On macOS, approve Keychain prompts for Chrome cookie access.

If Canvas host detection is ambiguous, set the base URL:

```bash
export CANVAS_BASE_URL=https://school.instructure.com
```

macOS may ask for Keychain access when reading Chrome cookies.

After changing auth settings, test with a small CLI read:

```bash
canvas courses --all --limit 5
```

## MCP Server

MCP is optional. Prefer the CLI unless an MCP-compatible client needs to call Canvas tools directly.

Run over stdio:

```bash
canvas-mcp --transport stdio
```

Run over HTTP:

```bash
canvas-mcp --transport http --host 127.0.0.1 --port 8000
```

HTTP endpoint:

```text
http://127.0.0.1:8000/mcp
```

Example MCP server command for clients that accept JSON config:

```json
{
  "mcpServers": {
    "canvas": {
      "command": "canvas-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

If your client needs an absolute command path, use the path returned by:

```bash
which canvas-mcp
```

## Common CLI Flow

Start by resolving the course ID:

```bash
canvas resolve "ENGL394" --all
canvas courses --all --search ENGL394
```

Then use that course ID with the relevant command:

```bash
canvas course context 12345
canvas assignments list 12345 --bucket upcoming
canvas assignments show 12345 67890 --include-submission
canvas assignments submissions install 12345 67890
canvas discussion show 12345 98765
```

For a Canvas URL, let the CLI parse it:

```bash
canvas url "https://school.instructure.com/courses/12345/assignments/67890"
```

## Tool Reference

The CLI examples below are the recommended way to use the project. Each tool can also be called through MCP or through the raw tool runner:

```bash
canvas tool list
canvas tool run list_courses --args '{"limit":10}'
```

Prefer first-class CLI commands when one exists. Use `canvas tool run` for MCP parity, quick debugging, scripting, or tools that do not have a dedicated command.

### `get_today`

Returns today's date in ISO format.

```bash
canvas today
canvas tool run get_today
```

Useful when comparing Canvas due dates against the current local date.

### `list_courses`

Lists courses for the current user. Favorites are returned by default.

```bash
canvas courses
canvas courses --all --search "data"
canvas tool run list_courses --args '{"favorites_only":false,"search":"data","limit":20}'
```

Useful when you need a course ID before calling course-specific tools.

### `resolve_course`

Fuzzy-matches a natural-language course query to likely Canvas courses.

```bash
canvas resolve "ENGL394" --all
canvas tool run resolve_course --args '{"query":"ENGL394","favorites_only":false,"limit":5}'
```

Useful when you know the course name, code, or nickname but not the Canvas course ID.

### `get_course_overview`

Returns course metadata.

```bash
canvas course overview 12345
canvas tool run get_course_overview --args '{"course_id":"12345"}'
```

Use this for a quick course identity check before fetching deeper content.

### `get_course_syllabus`

Returns syllabus metadata and, optionally, the syllabus body.

```bash
canvas course syllabus 12345
canvas course syllabus 12345 --no-body
canvas tool run get_course_syllabus --args '{"course_id":"12345","include_body":true,"body_char_limit":12000}'
```

Useful for extracting policies, weekly schedules, grading breakdowns, or instructor-provided course expectations.

### `get_course_context_snapshot`

Returns an aggregated course snapshot: overview, upcoming assignments, announcements, modules, and grade summary.

```bash
canvas course context 12345
canvas course context 12345 --body --upcoming-limit 10 --modules-limit 5
canvas tool run get_course_context_snapshot --args '{"course_id":"12345","upcoming_limit":10,"announcements_limit":5}'
```

Useful as a single starting point when an agent or script needs broad course context.

### `list_course_assignments`

Lists assignments for a course.

```bash
canvas assignments list 12345
canvas assignments list 12345 --bucket upcoming
canvas assignments list 12345 --search infographic --include-submission
canvas tool run list_course_assignments --args '{"course_id":"12345","bucket":"upcoming","include_submission":true,"limit":20}'
```

Useful for finding due work, locating an assignment ID, or checking submission status at a glance.

### `get_assignment_details`

Returns full details for one assignment, including description, submission settings, linked discussion metadata, and rubric fields when Canvas provides them.

```bash
canvas assignments show 12345 67890
canvas assignments show 12345 67890 --include-submission
canvas tool run get_assignment_details --args '{"course_id":"12345","assignment_id":"67890","include_submission":true}'
```

Useful before working on a specific assignment or checking whether Canvas has recorded your submission.

### `get_assignment_rubric`

Returns rubric criteria and settings for one assignment.

```bash
canvas assignments rubric 12345 67890
canvas assignments rubric 12345 67890 --include-assessment
canvas tool run get_assignment_rubric --args '{"course_id":"12345","assignment_id":"67890","include_assessment":true}'
```

Useful for turning grading criteria into a checklist or reviewing scored rubric feedback.

### `list_assignment_groups`

Lists assignment groups, optionally including assignments and submission data.

```bash
canvas assignments groups 12345
canvas assignments groups 12345 --assignments --include-submission
canvas tool run list_assignment_groups --args '{"course_id":"12345","include_assignments":true,"include_submission":true}'
```

Useful for understanding grade categories such as exams, projects, homework, and participation.

### `list_course_submissions`

Lists submissions for a student in a course. The default student is `self`.

```bash
canvas course submissions 12345
canvas course submissions 12345 --assignment 67890 --student-id self
canvas course submissions 12345 --workflow-state submitted
canvas tool run list_course_submissions --args '{"course_id":"12345","student_id":"self","assignment_ids":["67890"],"limit":20}'
```

Useful for checking submitted files, timestamps, comments, rubric assessments, and grade feedback. Non-self queries require Canvas permissions.

### `install_assignment_submission_files`

Downloads attachment files from the current user's submission for one assignment.

```bash
canvas assignments submissions install 12345 67890
canvas assignments submissions install 12345 67890 --force-refresh
canvas tool run install_assignment_submission_files --args '{"course_id":"12345","assignment_id":"67890","force_refresh":true}'
```

Useful for installing submitted files into a local assignment-scoped download folder. Attachments without Canvas file IDs are reported as skipped.

### `get_course_grade_summary`

Returns grade summary and assignment-group performance.

```bash
canvas course grades 12345
canvas course grades 12345 --student-id self
canvas tool run get_course_grade_summary --args '{"course_id":"12345","student_id":"self"}'
```

Useful for checking current standing and seeing which assignment groups affect the grade.

### `list_modules`

Lists course modules, optionally including module items and content details.

```bash
canvas course modules 12345
canvas course modules 12345 --items
canvas course modules 12345 --items --details --search "week 4"
canvas tool run list_modules --args '{"course_id":"12345","include_items":true,"include_content_details":true,"limit":20}'
```

Useful when courses organize readings, pages, assignments, and files by week or unit.

### `list_discussion_topics`

Lists discussion topics in a course.

```bash
canvas discussion list 12345
canvas discussion list 12345 --graded
canvas discussion list 12345 --search "week 2" --search-in title_or_message
canvas tool run list_discussion_topics --args '{"course_id":"12345","only_graded":true,"limit":20}'
```

Useful for finding a discussion topic ID before reading entries or matching graded discussions back to assignments.

### `get_discussion_entries`

Returns discussion entries, replies, and participant metadata for a topic.

```bash
canvas discussion show 12345 98765
canvas discussion show 12345 98765 --no-replies
canvas tool run get_discussion_entries --args '{"course_id":"12345","topic_id":"98765","include_replies":true,"limit":100}'
```

Useful for reading a thread, summarizing participation, or inspecting replies under a graded discussion.

### `list_course_pages`

Lists course wiki pages.

```bash
canvas course pages 12345
canvas course pages 12345 --search syllabus
canvas course pages 12345 --published
canvas tool run list_course_pages --args '{"course_id":"12345","search":"syllabus","published_only":true}'
```

Useful when course content is stored as Canvas pages rather than files or modules.

### `canvas_get_page`

Fetches one course wiki page by URL slug or page ID.

```bash
canvas course page 12345 course-schedule
canvas course page 12345 42 --force-as-id
canvas tool run canvas_get_page --args '{"course_id":"12345","url_or_id":"course-schedule"}'
```

Useful for reading a specific page after finding it with `list_course_pages`.

### `list_course_tabs`

Lists course navigation tabs.

```bash
canvas course tabs 12345
canvas tool run list_course_tabs --args '{"course_id":"12345","limit":50}'
```

Useful for discovering which Canvas sections are enabled in a course.

### `get_course_tab`

Returns one course navigation tab and can optionally resolve the target content.

```bash
canvas course tab 12345 modules
canvas course tab 12345 home --no-target
canvas tool run get_course_tab --args '{"course_id":"12345","tab_id":"modules","include_target":true}'
```

Useful when you want to inspect a course tab exactly as Canvas exposes it.

### `list_course_files`

Lists files for a course.

```bash
canvas files list 12345
canvas files list 12345 --search lecture --sort updated_at --order desc
canvas tool run list_course_files --args '{"course_id":"12345","search":"lecture","sort":"updated_at","order":"desc","limit":20}'
```

Useful for locating PDFs, slides, datasets, or handouts.

### `download_course_file`

Downloads a course file into local temp storage and returns the local path.

```bash
canvas files download 12345 55555
canvas files download 12345 55555 --force-refresh
canvas tool run download_course_file --args '{"course_id":"12345","file_id":"55555","force_refresh":true}'
```

Useful when a file needs to be parsed locally or handed to another command.

### `list_course_folders`

Lists folders for a course.

```bash
canvas files folders 12345
canvas tool run list_course_folders --args '{"course_id":"12345","limit":100}'
```

Useful for understanding file organization before listing or downloading files.

### `list_announcements`

Lists announcements for one or more courses.

```bash
canvas announcements --course 12345
canvas announcements --course 12345 --course 67890 --active
canvas tool run list_announcements --args '{"course_ids":["12345"],"active_only":true,"limit":20}'
```

Useful for checking recent instructor updates without opening each course manually.

### `list_todo_items`

Lists current user's Canvas To Do items, optionally filtered by course.

```bash
canvas todo
canvas todo --course 12345
canvas tool run list_todo_items --args '{"course_ids":["12345"],"limit":50}'
```

Useful for a quick pending-work view across Canvas.

### `list_course_people`

Lists users in a course, with optional role and search filters.

```bash
canvas course people 12345
canvas course people 12345 --role teacher
canvas course people 12345 --search "jane" --email
canvas tool run list_course_people --args '{"course_id":"12345","enrollment_types":["teacher"],"include_email":true}'
```

Useful for finding instructors, TAs, classmates, or enrollment metadata when your Canvas permissions allow it.

### `resolve_canvas_url`

Parses a Canvas URL into course/object identifiers and can optionally fetch details.

```bash
canvas url "https://school.instructure.com/courses/12345/assignments/67890"
canvas url "https://school.instructure.com/courses/12345/files/55555" --no-details
canvas tool run resolve_canvas_url --args '{"url":"https://school.instructure.com/courses/12345/assignments/67890","fetch_details":true}'
```

Useful when a user gives an agent or script a Canvas link instead of IDs.

## Agent Guidance

This repo ships a ready-to-use agent skill file at [`skills/canvas-cli/SKILL.md`](skills/canvas-cli/SKILL.md). Add it to your agent setup if you want the agent to prefer the CLI and follow the recommended Canvas workflow.

## Notes

- `canvas_get_page` only fetches wiki pages. Use `canvas url ...` for Canvas URLs whose type is unknown.
- Non-self submission queries require Canvas permissions for viewing other students.
- Current functionality is read-only.
