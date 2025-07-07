#! /bin/bash

# - Use this directory as the working directory for gemini-cli
#   so it can find .gemini/settings.json with correct MCP config.
# - ANON_TARGET mounts directory containing datasource file into MCP server
#   container. ANON_TARGET should not be inside gemini's working directory to
#   prevent it from reading sensitve data directly.

set -eu

ANON_TARGET=$(readlink -e ${ANON_TARGET:-"$PWD"})
if [ ! -d "$ANON_TARGET" ]; then
  >&2 echo 'ANON_TARGET must be a directory'
  exit 1
fi

exec docker compose run \
  --rm --build \
  -v "$PWD":/opt/app/workdir/host \
  -v "$ANON_TARGET":/opt/app/workdir/target \
  -p 8000:8000 \
  mcp-anon --transport http

