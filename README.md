# Python Hackathon Setup

[![CI](https://github.com/messeb/python-hackathon-setup/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/messeb/python-hackathon-setup/actions/workflows/ci.yml)
[![Publish](https://github.com/messeb/python-hackathon-setup/actions/workflows/publish.yml/badge.svg)](https://github.com/messeb/python-hackathon-setup/actions/workflows/publish.yml)
[![Security](https://github.com/messeb/python-hackathon-setup/actions/workflows/security.yml/badge.svg?branch=develop)](https://github.com/messeb/python-hackathon-setup/actions/workflows/security.yml)

A production-ready starter for AI hackathons and beyond:

- **FastAPI** backend managed with **uv**
- **LLM** endpoints with pluggable providers
- **PyTorch** endpoints
- **Vue 3** frontend
- **Git Flow** with release candidates, CI guardrails, and signed container images on **GHCR**

| Layer | Stack |
|---|---|
| Backend | Python 3.13 · uv · FastAPI · Pydantic v2 · pydantic-settings · Uvicorn |
| LLM | Anthropic Claude (official SDK, default model `claude-opus-5-5`) · any OpenAI-compatible server (OpenAI, Ollama, vLLM, LM Studio, LiteLLM) · offline `fake` provider |
| ML | PyTorch (CPU wheels via a dedicated uv index; GPU is a one-line change) |
| Frontend | Vue 3 · Vite · TypeScript · Pinia · Vue Router · Vitest |
| Quality | ruff · mypy `--strict` · pytest (≥ 85 % coverage) · oxlint · eslint · prettier · vue-tsc · pre-commit |
| Delivery | Multi-stage non-root Docker image · GHCR · SBOM + provenance + attestation · Dependabot · CodeQL |

## Quick start

Prerequisites: [uv](https://docs.astral.sh/uv/) ≥ 0.13, Node 24 and pnpm 12. Docker is optional.

```bash
make install          # uv sync + pnpm install
make dev-backend      # http://localhost:8000/api/docs
make dev-frontend     # http://localhost:5173 (proxies /api to the backend)
```

The app runs **without API keys**: the default `fake` LLM provider echoes your input.
To use a real model, copy `backend/.env.example` to `backend/.env` and choose one of these:

```bash
# Claude
APP_LLM_PROVIDER=anthropic
APP_ANTHROPIC_API_KEY=sk-ant-...
APP_LLM_MODEL=claude-opus-5-5       # optional; also: claude-sonnet-5-5, claude-haiku-5-5

# Local model via Ollama (or any OpenAI-compatible server)
APP_LLM_PROVIDER=openai
APP_OPENAI_BASE_URL=http://localhost:11434/v1
APP_LLM_MODEL=llama3.2
```

### Run the production container

```bash
docker compose up --build                                   # http://localhost:8000
# or a published image:
docker run -p 8000:8000 ghcr.io/messeb/python-hackathon-setup:latest
```

A single container serves both the API and the built Vue app. It runs as a non-root user, has a health check, and supports a read-only root filesystem.

## API

Interactive docs: `/api/docs` · OpenAPI schema: `/api/openapi.json`

| Method | Path | Description |
|---|---|---|
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | Readiness probe (LLM provider, torch device) |
| GET | `/api/v1/llm/info` | Active LLM provider and model |
| POST | `/api/v1/llm/chat` | Chat completion (`{"messages":[{"role":"user","content":"Hi"}]}`) |
| POST | `/api/v1/llm/chat/stream` | Same request, streamed as Server-Sent Events (`delta`… → `done` \| `error`) |
| GET | `/api/v1/ml/info` | PyTorch version, device, threads |
| POST | `/api/v1/ml/similarity` | Pairwise cosine-similarity matrix of vectors |
| POST | `/api/v1/ml/regression` | Fit `y = a·x + b` with autograd |
| GET/POST | `/api/v1/items` | List or create items |
| GET/PATCH/DELETE | `/api/v1/items/{id}` | Read, update or delete an item |

```bash
curl -N -X POST localhost:8000/api/v1/llm/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Tell me a joke"}]}'
```

## Project layout

```
├── backend/                     uv project (src layout)
│   ├── src/app/
│   │   ├── main.py              app factory, lifespan, SPA serving
│   │   ├── core/                settings (APP_* env vars), logging
│   │   ├── api/                 routers + dependency injection
│   │   ├── schemas/             Pydantic request/response models
│   │   └── services/
│   │       ├── llm/             LLMClient protocol + anthropic / openai / fake adapters
│   │       ├── ml/              PyTorch service
│   │       └── items.py         repository (swap for a DB)
│   └── tests/                   pytest; no network, providers are stubbed
├── frontend/                    Vue 3 + Vite + TS
│   └── src/{api,stores,views}/  typed API client + SSE parser, Pinia store, pages
├── Dockerfile                   node build → uv build → slim runtime
├── .github/workflows/           ci · gitflow · publish · security
├── scripts/                     bump-version.sh, check-version.sh
└── docs/GIT_FLOW.md             branching, RC and release process
```

### Configuration

All settings are environment variables with the `APP_` prefix. See `backend/src/app/core/config.py` and `backend/.env.example`.
Notable settings:

- `APP_LLM_EFFORT` (`low`…`max`) sets Claude's effort level.
- `APP_LLM_REFUSAL_FALLBACK` controls Claude's server-side refusal fallback. It is **on** by default.
- `APP_TORCH_DEVICE` picks the torch device (`auto` / `cpu` / `cuda` / `mps`).
- `APP_CORS_ORIGINS` sets the allowed CORS origins.

**GPU:** in `backend/pyproject.toml`, point the `pytorch-cpu` index URL at a CUDA index (for example `https://download.pytorch.org/whl/cu128`), then run `uv lock`.

## Development workflow

| Command | What it does |
|---|---|
| `make check` | lint + type-check + tests for backend and frontend (what CI runs) |
| `make format` | auto-fix lint and formatting |
| `make hooks` | install pre-commit hooks (linters, Conventional Commit messages, no direct commits to `main`/`develop`) |
| `make docker` | build and run the production image |

## Branching & releases

This repo follows **Git Flow** with release candidates. The full process is in **[docs/GIT_FLOW.md](docs/GIT_FLOW.md)**: features, bug fixes, RCs, production releases, and hotfixes.

```
feature/* ──squash──▶ develop ──▶ release/X.Y.Z ──tag vX.Y.Z-rc.N──▶ QA
                         ▲                │
                         └──back-merge── main ◀──merge── (approved RC) ──tag vX.Y.Z──▶ prod
```

| Event | Container image | GitHub |
|---|---|---|
| push to `develop` | `:develop`, `:sha-<short>` | – |
| tag `vX.Y.Z-rc.N` on `release/X.Y.Z` | `:X.Y.Z-rc.N` | pre-release |
| tag `vX.Y.Z` on `main` | `:X.Y.Z`, `:X.Y`, `:latest` | release |

## CI/CD guardrails

- **CI** (`ci.yml`): checks the backend (ruff, mypy, pytest + coverage gate) and the frontend (prettier, oxlint, eslint, vue-tsc, vitest, build). It also builds the Docker image, smoke-tests it, and lints the workflows (actionlint, zizmor). The single required check is **`CI passed`**.
- **Git Flow** (`gitflow.yml`): enforces which branches may merge where, checks version and CHANGELOG consistency on release PRs, and requires Conventional Commit PR titles.
- **Publish** (`publish.yml`): validates tags, re-runs CI, then builds and pushes a multi-arch image with SBOM, provenance and attestation, and creates the GitHub (pre-)release.
- **Security** (`security.yml`): CodeQL for Python, TypeScript and Actions, plus dependency review on PRs. Dependabot opens weekly grouped PRs into `develop`.
- **Repository rulesets**: protect `main`, `develop`, `release/*`, `hotfix/*` and the `v*` tags. See [GIT_FLOW §8](docs/GIT_FLOW.md#8-guardrails-reference).

## License

[MIT](LICENSE)
