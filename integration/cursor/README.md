# Integration with cursor

## Install cursor

Select installer from https://www.cursor.com/downloads

## Start mcp-anon server locally

```bash
cd integration/cursor
bash start-mcp-anon-with-http.sh
```

## Start cursor

Cursor reads
[MCP configuration](https://docs.cursor.com/context/mcp#configuration-locations)
from either project specific `.cursor/mcp.json` file
or from global `~/.cursor/mcp.json` file in home directory.

This integration guide comes with an example
`integration/cursor/.cursor/mcp.json`.
You can use this file directly by running cursor in
`integration/cursor` directory.

