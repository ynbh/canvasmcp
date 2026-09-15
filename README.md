# canvas-cli

Local Canvas LMS access for the terminal, coding agents, and optional MCP clients.

- `canvas` — CLI (preferred)
- `canvas-mcp` — same tools over MCP
- Auth is your existing Chrome Canvas session

Agent skill: [`skills/canvas-cli/SKILL.md`](skills/canvas-cli/SKILL.md). Full command table: [`docs/cli.md`](docs/cli.md).

## Install

```bash
uv tool install git+https://github.com/ynbh/canvasmcp.git
canvas --help
```

Pin a ref with `@main` or `@<tag-or-commit>`. Local dev: `uv sync` then `uv run canvas --help`.

## Auth

Log in to Canvas in Chrome, then:

```bash
canvas auth-status
```

If that fails: `canvas settings profiles`, `canvas settings choose-profile`, or `export CANVAS_BASE_URL=https://school.instructure.com`. On macOS, approve Keychain prompts. Then `canvas courses --all --limit 5`.

## CLI

```bash
canvas resolve "ENGL394" --all
canvas course context 12345
canvas assignments list 12345 --bucket upcoming
canvas assignments show 12345 67890 --include-submission
canvas url "https://school.instructure.com/courses/12345/assignments/67890"
```

`canvas --help` is the source of truth for flags. Raw tools: `canvas tool list` and `canvas tool run <name> --args '{...}'`.

## Output

Terminal output uses readable lists and details; redirected output is compact JSON. Override with a global option before the command:

```bash
canvas --output pretty assignments submissions scheduled
canvas --output json courses
export CANVAS_OUTPUT=json  # Consistent agent output, including through a PTY
```

`--output auto|pretty|json` overrides `CANVAS_OUTPUT`. Low-level `tool` commands and hidden scheduler execution default to JSON even in a terminal. Explicit JSON preserves the full response; pretty views omit routine metadata and mark that omission.

Operational errors are structured JSON on stdout in JSON mode, or readable diagnostics on stderr in pretty mode. Refused previews exit 1; invalid tool arguments exit 2. Auth-status/settings inspection still reports its status without failing the command. Framework help and option parsing errors retain Typer's normal text format. JSON profile selection requires an explicit profile name and never prompts.

## MCP

Optional. Prefer the CLI unless a client needs MCP.

```bash
canvas-mcp --transport stdio
canvas-mcp --transport http --host 127.0.0.1 --port 8000
```

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
