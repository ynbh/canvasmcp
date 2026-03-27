---
name: canvas-cli
description: Use the local `canvas` CLI for Canvas LMS workflows in this repository. Trigger when you need to resolve a course, list modules, assignments, discussions, files, pages, people, grades, announcements, calendar items, or inspect Canvas auth status from the terminal. Prefer this skill over direct API inspection when the task is about operating the existing CLI effectively and safely.
---

# Canvas CLI

Use `uv run canvas ...` from the repo root.

This skill is for using the existing CLI well, not for editing the CLI itself.

## Core rules

- Prefer `uv run canvas resolve <query>` before using a course-specific command.
- Prefer course IDs from CLI output instead of guessing or hardcoding them.
- Keep output machine-readable. Do not add shell pipes like `| jq` unless the user explicitly wants shell formatting.
- Use `--items` for module inspection when the user needs module contents, not just module names.
- Use `canvas tool run` only as an escape hatch when no first-class subcommand exists.
- For auth checks, use `uv run canvas auth-status` before assuming the CLI is broken.
- Do not expose cookie values, tokens, or raw browser storage in summaries.

## Fast paths

Resolve a course:

```bash
uv run canvas resolve ENGL394
```

List matching courses:

```bash
uv run canvas courses --all --search ENGL394
```

List modules:

```bash
uv run canvas course modules 1402756
uv run canvas course modules 1402756 --items
```

List assignments:

```bash
uv run canvas assignments list 1402756
uv run canvas assignments show 1402756 7533743
```

List discussions:

```bash
uv run canvas discussion list 1402756
uv run canvas discussion show 1402756 5941408
```

List and download files:

```bash
uv run canvas files list 1402756
uv run canvas files download 1402756 87850971
```

Inspect course context:

```bash
uv run canvas course overview 1402756
uv run canvas course context 1402756
```

Check auth:

```bash
uv run canvas auth-status
```

## Recommended workflow

1. Resolve the course by code or title.
2. Confirm the course ID from the returned JSON.
3. Run the narrowest command that answers the question.
4. If the user asks for explanation, summarize the returned JSON in prose.
5. If the user asks for a document summary, download the file and inspect it locally.

## Common tasks

Find a class and list its modules:

```bash
uv run canvas resolve MATH401
uv run canvas course modules <course_id> --items
```

Check if a course uses modules or other surfaces:

```bash
uv run canvas course modules <course_id>
uv run canvas assignments list <course_id>
uv run canvas files list <course_id>
uv run canvas course pages <course_id>
```

Find announcements or calendar items across courses:

```bash
uv run canvas announcements --course 1402756
uv run canvas calendar --course 1402756
```

Use a raw tool when needed:

```bash
uv run canvas tool list
uv run canvas tool run resolve_canvas_url --args '{"url":"https://umd.instructure.com/courses/1402756/assignments/7533743"}'
```

## Auth and failure handling

- `auth_mode: "chrome-session"` means the CLI found a usable Chrome-backed Canvas session.
- `configured_canvas_base_url` is only an override. It should not be the default recommendation unless auto-detection is ambiguous.
- `detected_canvas_domains` are safe to report. They help diagnose multi-school Chrome sessions.
- If auto-detection fails, tell the user what Chrome domains were detected and suggest opening the target Canvas site in Chrome first.
- If a command fails for auth reasons, prefer a concise explanation over a traceback.

## Good response patterns

- For course lookup, include the resolved course name and ID.
- For module listing, summarize module names first, then notable items if `--items` was used.
- For downloaded files, report the local path and then summarize the document contents.
- When no data exists, say so directly, for example: "This course currently has no Canvas modules."

## Avoid

- Avoid guessing course IDs.
- Avoid assuming a course uses Modules; many instructors use Assignments, Files, or Pages instead.
- Avoid reporting raw JSON unless the user asked for it.
- Avoid telling the user to set `CANVAS_BASE_URL` first when Chrome auto-detection should normally work.
