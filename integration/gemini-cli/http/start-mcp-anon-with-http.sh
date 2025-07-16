#! /bin/bash

export UID

exec docker compose up --build mcp-anon-http

