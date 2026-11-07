# syntax=docker/dockerfile:1.10
# Multi-stage build: Vue SPA + uv-managed FastAPI/PyTorch app in one slim, non-root image.

ARG PYTHON_VERSION=3.13
ARG NODE_VERSION=24
ARG UV_VERSION=0.13.7
ARG PNPM_VERSION=12.3.4

# ---- uv binary (pinned) ------------------------------------------------------
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# ---- 1. Frontend build -------------------------------------------------------
FROM node:${NODE_VERSION}-slim AS frontend
ARG PNPM_VERSION
WORKDIR /src
RUN npm install --global --no-fund --no-audit "pnpm@${PNPM_VERSION}"
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build-only

# ---- 2. Python dependencies + app ---------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS backend
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src
# Dependencies first (cached layer), project second.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# ---- 3. Runtime ----------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=backend --chown=app:app /app/.venv /app/.venv
COPY --from=frontend --chown=app:app /src/dist /app/static
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENVIRONMENT=production \
    APP_STATIC_DIR=/app/static
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=4)"]
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
