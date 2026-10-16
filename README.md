# canvas-cli

Use Canvas LMS from your terminal. Check what's due, read assignments, announcements, and your inbox, download course files, and submit work, all without opening a browser tab.

It signs in with the Canvas session already in your browser, so there's no API token to create. It ships as two commands:

- `canvas`: the CLI.
- `canvas-mcp`: the same tools as an MCP server, for chat clients that need one.

If you're setting up a coding agent, point it at [`skills/canvas-cli/SKILL.md`](skills/canvas-cli/SKILL.md).

## Install

```bash
uv tool install git+https://github.com/ynbh/canvasmcp.git
```

Add `@<tag-or-commit>` to the URL to pin a version. To work on the code instead, run `uv sync`, then `uv run canvas`.

## Sign in

Log in to Canvas in Chrome, then check that the CLI can see your session:

```bash
canvas auth-status
```

On macOS, allow the Keychain prompt; the CLI needs it to read Chrome's cookies. If the check fails:

- **You use more than one Chrome profile:** run `canvas settings choose-profile` to pick the one you use for Canvas.
- **The CLI can't work out your school's Canvas address:** set it yourself with `export CANVAS_BASE_URL=https://school.instructure.com`.

**Firefox:** log in there, then set `CANVAS_COOKIE_BROWSER=firefox` along with `CANVAS_BASE_URL`.

**No browser on the machine:** set `CANVAS_SESSION_COOKIE` and `CANVAS_CSRF_TOKEN` (plus `CANVAS_BASE_URL`), copied from a logged-in browser. These are your login, so keep them out of files, shell history, and chats.

## Look things up

```bash
canvas todo                                    # what Canvas says you need to do
canvas resolve "ENGL394"                       # find a course ID by name or code
canvas assignments list 12345 --bucket upcoming
canvas assignments show 12345 67890
canvas announcements --course 12345
canvas inbox list --scope unread               # reading never marks messages read
canvas files download 12345 555
canvas url "https://school.instructure.com/courses/12345/assignments/67890"
```

`canvas url` takes any Canvas link and tells you what it points to. Run `canvas --help` on any command for its options, or see [every command](docs/cli.md).

## Submit an assignment

A submission takes two steps. First, preview it, which shows exactly what will be sent and prints a token:

```bash
canvas assignments submissions preview 12345 67890 --type online_upload --file essay.pdf --now
```

Then confirm with that token. Nothing reaches Canvas until you do:

```bash
canvas assignments submissions confirm <token>
```

To submit later instead, replace `--now` with `--at 2026-10-20T23:00:00-04:00` or `--minutes-before-due 30`. Scheduled submissions run in the background on macOS, even if the terminal is closed. The Mac does need to be awake at submit time; add `--caffeinate` when you confirm to keep it awake until then. To manage them:

- **List them:** `canvas assignments submissions scheduled`
- **Cancel one:** `canvas assignments submissions cancel <job>`

## Scripts and agents

In a terminal you get readable output. When the output is piped or redirected, you get compact JSON instead. To force one or the other, use `--output pretty` or `--output json` before the command, or set `CANVAS_OUTPUT=json`.

When a command fails, it exits with status 1, or 2 if the arguments were bad. In JSON mode, the error comes as `{"error": ..., "message": ...}`. `canvas auth-status` is the exception: it always succeeds and reports the problem in its output.

To call any tool directly with JSON arguments:

```bash
canvas tool list
canvas tool run list_courses --args '{"limit": 5}'
```

## MCP

Use the CLI unless your client only speaks MCP. To add the server to a client:

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

For HTTP, run `canvas-mcp --transport http --host 127.0.0.1 --port 8000`. Tools that only read are marked read-only, so clients can choose to skip their approval prompt. Submitting and cancelling are marked destructive.
