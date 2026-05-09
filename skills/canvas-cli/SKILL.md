---
name: canvas-cli
description: Use the local `canvas` CLI for Canvas LMS workflows. Trigger when you need to find a course, inspect modules/assignments/discussions/files/pages/people/grades/rubrics, or verify Canvas session status from the terminal.
---

# Canvas CLI Agent Instructions

Run commands with the installed `canvas` executable. Prefer first-class `canvas` subcommands over raw tool calls. Use `uv run canvas` only when working inside this repository before installation.

## Rules

- Resolve a course before using course-scoped commands unless the user provided a course ID.
- Use the narrowest first-class CLI command that answers the request.
- Use `canvas tool run` only when no first-class subcommand exists, for debugging, or to mirror MCP tool behavior.
- Preserve user privacy: never print cookie values, CSRF tokens, access tokens, or raw auth headers.
- Summarize JSON output for the user. Do not paste large raw JSON unless requested.
- Include exact IDs when they help the user follow up: `course_id`, `assignment_id`, `topic_id`, `file_id`.
- If no matching Canvas object is found, say that directly and mention the search term/course checked.
- If auth fails, run the auth recovery workflow before treating it as a code issue.
- Treat quiz support as read-only.

## Auth

```bash
canvas auth-status
canvas settings profiles
canvas settings choose-profile "<profile-name>"
canvas settings show
canvas settings clear
```

Use `auth-status` first when any Canvas command fails unexpectedly.

Auth recovery workflow:

- Confirm the user is logged in to Canvas in Chrome, then rerun `canvas auth-status`.
- If multiple Chrome profiles exist, run `canvas settings profiles`, choose the profile with Canvas cookies, then rerun `canvas auth-status`.
- If the saved profile is stale or wrong, run `canvas settings clear`, then choose the profile again.
- If Canvas host detection is wrong, use `CANVAS_BASE_URL=https://school.instructure.com` for subsequent commands.
- On macOS, Keychain prompts for Chrome cookie access must be approved.

## Course Resolution

```bash
canvas resolve "ENGL394" --all
canvas courses --all --search ENGL394
canvas tool run resolve_course --args '{"query":"ENGL394","favorites_only":false,"limit":10}'
```

Best practice:

- Prefer `canvas resolve` for user-provided names like "ENGL394" or "business writing".
- Use `favorites_only=false` when the user expects all active/past courses to be considered.
- Confirm the resolved course name when multiple courses could match.

## Assignments

```bash
canvas assignments list <course_id> --search infographic --limit 20
canvas assignments list <course_id> --bucket upcoming
canvas assignments list <course_id> --search infographic --include-submission
canvas assignments show <course_id> <assignment_id> --include-submission
canvas assignments groups <course_id> --assignments --include-submission
```

Best practice:

- Search assignments by keyword before fetching details when the assignment ID is unknown.
- Use `assignments show` for instructions, due dates, submission settings, discussion links, and attached rubric fields.
- Use assignment aliases only as lookup aids; report canonical assignment IDs in final answers.

## Rubrics

```bash
canvas assignments rubric <course_id> <assignment_id>
canvas assignments rubric <course_id> <assignment_id> --include-assessment
```

Best practice:

- Use `assignments rubric` when the user asks for grading criteria, rubric categories, points, or how an assignment will be evaluated.
- Use `--include-assessment` only when the user asks how they were graded or wants rubric feedback for their own submission.
- Report rubric title, total points, criteria names, point values, and rating levels.
- Do not assume `use_rubric_for_grading=true`; report its value if relevant.
- If the assignment has no rubric, say so and suggest checking assignment details/comments instead.

Example workflow:

```bash
canvas resolve "ENGL394" --all
canvas assignments list 1402756 --search infographic --limit 20
canvas assignments rubric 1402756 7543238
```

## Discussions

```bash
canvas discussion list <course_id>
canvas discussion list <course_id> --search planning
canvas discussion list <course_id> --graded
canvas discussion list <course_id> --search "week 2" --search-in title_or_message
canvas discussion show <course_id> <topic_id>
canvas discussion show <course_id> <topic_id> --no-replies
```

Best practice:

- If a discussion is assignment-linked, assignment search may be more reliable than discussion search.
- Use returned `discussion_topic_id` from assignment results to fetch entries.

## Files

```bash
canvas files list <course_id>
canvas files list <course_id> --search syllabus
canvas files list <course_id> --search lecture --sort updated_at --order desc
canvas files download <course_id> <file_id>
canvas files download <course_id> <file_id> --force-refresh
canvas files folders <course_id>
```

Best practice:

- Use `files download` only for Canvas course files with a `file_id`.
- Submission attachments may appear under `course submissions`; do not assume they are downloadable through `files download` until a file ID is present.

## Grades And Submissions

```bash
canvas course grades <course_id>
canvas course submissions <course_id> --student-id self
canvas course submissions <course_id> --assignment <assignment_id> --student-id self
canvas course submissions <course_id> --workflow-state submitted
```

Best practice:

- Use `student-id self` for the current user.
- Non-self submission queries may fail because of Canvas permissions; report permission limits clearly.
- For feedback questions, inspect submissions for `submission_comments`, `rubric_assessment`, `attachments`, `score`, `grade`, `late`, and `missing`.

## Course Structure

```bash
canvas course overview <course_id>
canvas course syllabus <course_id>
canvas course syllabus <course_id> --no-body
canvas course context <course_id>
canvas course modules <course_id> --items
canvas course modules <course_id> --items --details --search "week 4"
canvas course pages <course_id>
canvas course page <course_id> <page-url-or-id>
canvas course tabs <course_id>
canvas course tab <course_id> modules
canvas course people <course_id> --email
```

Best practice:

- Use `course context` when broad course context is needed quickly.
- Use `course syllabus` for course policies, grading breakdowns, or syllabus body content.
- Use modules for "what do I need to do next?" questions.
- Use pages/tabs when the user asks for resources or course navigation content.

## To Do And Announcements

```bash
canvas announcements --course <course_id>
canvas announcements --course <course_id> --course <other_course_id> --active
canvas todo
canvas todo --course <course_id>
```

Best practice:

- Use todo for the user's current Canvas To Do list and cross-course upcoming work.
- Use assignment APIs for full assignment details; todo entries are summaries.

## URL Lookup

```bash
canvas url "https://school.instructure.com/courses/<course_id>/assignments/<assignment_id>"
canvas url "https://school.instructure.com/courses/<course_id>/files/<file_id>" --no-details
```

Best practice:

- Use URL lookup when the user provides a Canvas URL.
- Follow the returned recommended tool when `fetch_details` is not enough.

## Raw Tool Escape Hatch

```bash
canvas tool list
canvas tool run <tool_name> --args '{"course_id":"12345"}'
```

Use this for newly added MCP tools before a first-class CLI command exists.
