#! /bin/bash

# - Use this repo root as the working directory for gemini-cli
#   so it can find .gemini/settings.json with this MCP server config.
# - Mount directory containing datasource file into MCP server container.
#   The datasource file should not be inside gemini-cli's working directory
#   if you do not trust gemini with the data.

set -eu
HERE=$(readlink -e "$(dirname "$BASH_SOURCE")")

ANON_TARGET=$(readlink -e ${ANON_TARGET:-"$PWD"})
if [ ! -d "$ANON_TARGET" ]; then
  >&2 echo 'ANON_TARGET must be a directory'
  exit 1
fi

exec docker compose -f "$HERE"/../../../docker-compose.yaml run \
  --rm --build \
  -v "$PWD":/opt/app/workdir/host \
  -v "$ANON_TARGET":/opt/app/workdir/target \
  mcp-anon

