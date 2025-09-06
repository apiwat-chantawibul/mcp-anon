FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
WORKDIR /opt/app
COPY pyproject.toml uv.lock ./
# Install essential dependencies
RUN \
  --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-install-project --no-dev


FROM base AS dev
# Install full dependencies for development version
RUN \
  --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-install-project
# Install application source code
COPY README.md ./
COPY src src/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked
ENV PATH="/opt/app/.venv/bin:$PATH"
ENV FASTMCP_HOST=0.0.0.0
# Prepare universally accessible workdirs
RUN chmod 777 src/tests/workdir
WORKDIR /opt/app/workdir
RUN chmod 777 .
# Switch to non-root executing user
USER 1000:1000
ENTRYPOINT ["fastmcp", "run", "../src/mcp_anon/server.py:app"]
CMD []


FROM base AS prod-builder
COPY README.md ./
# Skip tests code
# TODO: Use --exclude when supported in stable version of Dockerfile
COPY src/mcp_anon src/mcp_anon
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM python:3.13-slim-bookworm AS prod
COPY --from=prod-builder /opt/app /opt/app
ENV PATH="/opt/app/.venv/bin:$PATH"
ENV FASTMCP_HOST=0.0.0.0
WORKDIR /opt/app/workdir
RUN chmod 777 .
USER 1000:1000
WORKDIR /opt/app/workdir
ENTRYPOINT ["fastmcp", "run", "../src/mcp_anon/server.py:app"]
CMD []

