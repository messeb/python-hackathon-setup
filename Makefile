# Developer entrypoints. `make help` lists targets.
.DEFAULT_GOAL := help
SHELL := /bin/bash

BACKEND := backend
FRONTEND := frontend

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install backend + frontend dependencies
	cd $(BACKEND) && uv sync
	cd $(FRONTEND) && pnpm install

.PHONY: hooks
hooks: ## Install git pre-commit hooks
	uvx pre-commit install --hook-type pre-commit --hook-type commit-msg

.PHONY: dev-backend
dev-backend: ## Run FastAPI with auto-reload on :8000
	cd $(BACKEND) && uv run fastapi dev src/app/main.py --port 8000

.PHONY: dev-frontend
dev-frontend: ## Run Vite dev server on :5173 (proxies /api to :8000)
	cd $(FRONTEND) && pnpm dev

.PHONY: lint
lint: ## Lint + format-check everything
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check .
	cd $(FRONTEND) && pnpm lint && pnpm format:check

.PHONY: format
format: ## Auto-format everything
	cd $(BACKEND) && uv run ruff check --fix . && uv run ruff format .
	cd $(FRONTEND) && pnpm lint:fix && pnpm format

.PHONY: typecheck
typecheck: ## Static type checks
	cd $(BACKEND) && uv run mypy
	cd $(FRONTEND) && pnpm type-check

.PHONY: test
test: ## Run all tests
	cd $(BACKEND) && uv run pytest
	cd $(FRONTEND) && pnpm test

.PHONY: check
check: lint typecheck test ## Everything CI runs (except the container build)

.PHONY: docker
docker: ## Build and run the production image on :8000
	docker compose up --build
