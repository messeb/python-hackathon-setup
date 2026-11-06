# Contributing

1. Read the branching and release rules in **[docs/GIT_FLOW.md](docs/GIT_FLOW.md)**.
2. Set up: `make install && make hooks` (needs [uv](https://docs.astral.sh/uv/) ≥ 0.13,
   Node 24 and pnpm 12).
3. Branch from `develop`: `feature/<ticket>-<slug>` or `bugfix/<ticket>-<slug>`.
4. Run `make check` before pushing. CI runs the same gates.
5. Open a PR into `develop`. The title must be a [Conventional Commit](https://www.conventionalcommits.org/)
   (`feat: …`, `fix: …`), because it becomes the squash commit message.
6. Add a line to `CHANGELOG.md` under `## [Unreleased]` for user-facing changes.

## Code standards

- **Backend:** ruff (lint + format), mypy `--strict`, pytest with ≥ 85 % branch coverage.
  Routes depend on interfaces (`LLMClient`, `TorchService`), never on SDKs directly.
- **Frontend:** Composition API with `<script setup lang="ts">`, oxlint + eslint, prettier,
  vue-tsc, vitest. Never call `fetch` outside `src/api/`.
