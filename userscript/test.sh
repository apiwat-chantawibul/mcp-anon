#! /bin/bash

set -eux
HERE=$(readlink -e "$(dirname "$BASH_SOURCE")")
cd "$HERE"/..

docker compose run \
  --rm --build \
  test "$@"

