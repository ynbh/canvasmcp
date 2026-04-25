---
name: canvas-cli
description: Use the local `canvas` CLI for Canvas LMS workflows. Trigger when you need to find a course, inspect modules/assignments/discussions/files/pages/people/grades/rubrics, or verify Canvas session status from the terminal.
---

# Canvas CLI Agent Instructions

Run commands with the installed `canvas` executable. Use `uv run canvas` only when working inside this repository before installation.

## Rules

- Resolve a course before using course-scoped commands unless the user provided a course ID.
- Use the narrowest first-class CLI command that answers the request.
- Use `canvas tool run` only when no first-class subcommand exists.
- Preserve user privacy: never print cookie values, CSRF tokens, access tokens, or raw auth headers.
- Summarize JSON output for the user. Do not paste large raw JSON unless requested.
- Include exact IDs when they help the user follow up: `course_id`, `assignment_id`, `topic_id`, `file_id`.
- If no matching Canvas object is found, say that directly and mention the search term/course checked.
- If auth fails, run the auth recovery workflow before treating it as a code issue.

## Auth

```bash
canvas auth-status
canvas settings show
canvas settings profiles
canvas settings choose-profile "<profile-name>"
```

Use `auth-status` first when any Canvas command fails unexpectedly.

## Course Resolution

```bash
canvas tool run resolve_course --args '{"query":"ENGL394","favorites_only":false,"limit":10}'
canvas courses --all --search ENGL394
```

Best practice:

- Prefer `resolve_course` for user-provided names like "ENGL394" or "business writing".
- Use `favorites_only=false` when the user expects all active/past courses to be considered.
- Confirm the resolved course name when multiple courses could match.

## Assignments

```bash
canvas assignments list <course_id> --search infographic --limit 20
canvas assignments list <course_id> --bucket upcoming
canvas assignments show <course_id> <assignment_id>
canvas assignments groups <course_id> --assignments
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
canvas tool run resolve_course --args '{"query":"ENGL394","favorites_only":false,"limit":10}'
canvas assignments list 1402756 --search infographic --limit 20
canvas assignments rubric 1402756 7543238
```

## Discussions

```bash
canvas discussion list <course_id>
canvas discussion list <course_id> --search planning
canvas discussion show <course_id> <topic_id>
```

Best practice:

- If a discussion is assignment-linked, assignment search may be more reliable than discussion search.
- Use returned `discussion_topic_id` from assignment results to fetch entries.

## Files

```bash
canvas files list <course_id>
canvas files list <course_id> --search syllabus
canvas files download <course_id> <file_id>
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
```

Best practice:

- Use `student-id self` for the current user.
- Non-self submission queries may fail because of Canvas permissions; report permission limits clearly.
- For feedback questions, inspect submissions for `submission_comments`, `rubric_assessment`, `attachments`, `score`, `grade`, `late`, and `missing`.

## Course Structure

```bash
canvas course overview <course_id>
canvas course modules <course_id> --items
canvas course pages <course_id>
canvas course tabs <course_id>
canvas course people <course_id> --email
```

Best practice:

- Use modules for "what do I need to do next?" questions.
- Use pages/tabs when the user asks for syllabus, resources, or course navigation content.

## Calendar And Announcements

```bash
canvas announcements --course <course_id>
canvas calendar --course <course_id>
canvas calendar --course <course_id> --type assignment
```

Best practice:

- Use calendar for date-range questions and cross-course agenda questions.
- Use assignment APIs for full assignment details; calendar entries are summaries.

## URL Lookup

```bash
canvas url "https://umd.instructure.com/courses/<course_id>/assignments/<assignment_id>"
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
