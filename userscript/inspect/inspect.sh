#! /bin/bash

# Save fastmcp inspection report to file

# can be either `fastmcp` or `mcp`
FORMAT=${FORMAT:-fastmcp}

export UID

docker compose run \
  -i -t --rm --build \
  --entrypoint fastmcp \
  mcp-anon \
  inspect '../src/mcp_anon/server.py:app' \
    -f "$FORMAT" \
    -o pipeline/server-info."$FORMAT".json

