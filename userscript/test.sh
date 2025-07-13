#! /bin/bash

docker compose run \
  --rm --build \
  test "$@"

