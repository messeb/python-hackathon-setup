# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/). Release flow: [docs/GIT_FLOW.md](docs/GIT_FLOW.md).

## [Unreleased]

### Security

- Pin patched `minimatch` (GHSA-g3hv-75wg-m249) and `glob` (GHSA-3g3m-2fjr-6pw4) in the frontend toolchain via pnpm overrides.

### Added

- FastAPI backend managed by uv (Python 3.13) with an app factory, typed settings and JSON logging.
- REST endpoints: health probes (`/health/live`, `/health/ready`) and items CRUD (`/api/v1/items`).
- LLM endpoints (`/api/v1/llm/chat`, streaming `/api/v1/llm/chat/stream` over SSE) with pluggable
  providers: Anthropic Claude (default model `claude-opus-5-5`, server-side refusal fallback),
  any OpenAI-compatible server (OpenAI, Ollama, vLLM, ...), and an offline `fake` provider.
- PyTorch endpoints (`/api/v1/ml/info`, `/similarity`, `/regression`) on CPU wheels.
- Vue 3 + Vite + TypeScript frontend (Pinia, Vue Router) for status, streaming chat, ML demos and items.
- Multi-stage, non-root Docker image serving API and SPA from one container.
- CI (lint, types, tests, coverage gate, container smoke test, workflow lint), Git Flow guardrails,
  CodeQL, dependency review, Dependabot, and GHCR publishing with SBOM, provenance and attestations.
- Release documentation for feature, bugfix, RC, production and hotfix flows.

[Unreleased]: https://github.com/messeb/python-hackathon-setup/commits/develop
