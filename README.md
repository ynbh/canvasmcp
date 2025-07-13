# test

To install dependencies:

```bash
bun install
```

To run:

```bash
bun run index.ts


```

RUN MCP WITH: 
``` 
npx @modelcontextprotocol/inspector node mcp-server.js

```

add env var in the browser to test the tools

FOR MCP SET UP:

```json
{
    "mcpServers": {
        "canvas-lms": {
            "command": "node",
            "args": ["mcp-server.js"],
            "env": {
                "CANVAS_API_TOKEN": "whatever"
            }
        }
    }
}
```

This project was created using `bun init` in bun v1.2.18. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.
