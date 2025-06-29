#! /bin/bash

# Update Python requirement lock written in `pip-freeze.txt`.

set -eux
HERE=$(readlink -e "$(dirname "$BASH_SOURCE")")
cd "$HERE"/..

SERVICE=mcp-anon

# Clear `pip-freeze.txt` to build entirely with `requirements.txt`
> pip-freeze.txt

docker compose build \
  "$SERVICE"

docker compose run \
  --rm --quiet-pull \
  --entrypoint 'pip freeze' \
  "$SERVICE" \
  > pip-freeze.txt

