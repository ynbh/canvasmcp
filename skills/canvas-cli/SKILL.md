---
name: canvas-cli
description: Use the local `canvas` CLI for Canvas LMS workflows. Trigger when you need to find a course, inspect modules/assignments/discussions/files/pages/people/grades, or verify Canvas session status from the terminal.
---

# Canvas CLI

Use `uv run canvas ...` from the repo root.

This skill is for fast, accurate CLI usage. Focus on user outcomes, not internals.

## Operating principles

- Resolve the course first, then run course-scoped commands.
- Prefer the narrowest command that answers the question.
- Keep outputs machine-readable unless the user asks for formatted shell output.
- Use `canvas tool run` only when no first-class command exists.
- When auth fails, diagnose with `auth-status` and `settings` before assuming a code issue.

## Quick start

Find the course:

```bash
uv run canvas resolve ENGL394
```

List courses:

```bash
uv run canvas courses --all --search ENGL394
```

Check auth/session:

```bash
uv run canvas auth-status
uv run canvas settings profiles
```

## Common workflows

Inspect course structure:

```bash
uv run canvas course overview <course_id>
uv run canvas course modules <course_id>
uv run canvas course modules <course_id> --items
uv run canvas course pages <course_id>
```

Work with assignments:

```bash
uv run canvas assignments list <course_id>
uv run canvas assignments show <course_id> <assignment_id>
uv run canvas assignments groups <course_id> --assignments
```

Work with discussions:

```bash
uv run canvas discussion list <course_id>
uv run canvas discussion show <course_id> <topic_id>
```

Files and downloads:

```bash
uv run canvas files list <course_id>
uv run canvas files download <course_id> <file_id>
uv run canvas files folders <course_id>
```

People and grades:

```bash
uv run canvas course people <course_id> --email
uv run canvas course grades <course_id>
uv run canvas course submissions <course_id> --student-id self
```

Cross-course calendar/announcements:

```bash
uv run canvas announcements --course <course_id>
uv run canvas calendar --course <course_id>
```

URL-driven lookup:

```bash
uv run canvas url "https://.../courses/<id>/assignments/<id>"
```

## Auth recovery workflow

1. Run `uv run canvas auth-status`.
2. If session is not usable, run `uv run canvas settings profiles`.
3. Select the correct Chrome profile:

```bash
uv run canvas settings choose-profile
# or headless:
uv run canvas settings choose-profile "<profile-name>"
```

4. Re-check:

```bash
uv run canvas settings show
uv run canvas auth-status
```

## Tool escape hatch

When a first-class subcommand is missing:

```bash
uv run canvas tool list
uv run canvas tool run <tool_name> --args '{"course_id":"12345"}'
```

## Response guidance

- Include resolved `course_id` and course name when relevant.
- Summarize key findings from JSON in plain language.
- If nothing is found, state that directly.
- Never expose cookie/token values.
