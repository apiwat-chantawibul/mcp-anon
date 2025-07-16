#! /bin/bash

# Save fastmcp inspection report to file

export UID

docker compose run \
  -i -t --rm --build \
  --entrypoint fastmcp \
  mcp-anon \
  inspect '../src/app/server.py:app' -o pipeline/server-info.json

