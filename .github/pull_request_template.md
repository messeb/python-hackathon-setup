## What & why

<!-- One or two sentences. Link the ticket: Closes #123 -->

## Type

- [ ] `feat` new feature → `develop`
- [ ] `fix` bug fix → `develop` / `release/*` / `hotfix/*`
- [ ] `release` release or hotfix → `main`
- [ ] other (`chore`, `docs`, `refactor`, `test`, `ci`, `build`)

## Checklist

- [ ] PR title is a Conventional Commit (it becomes the squash commit)
- [ ] Tests added or updated; `make check` passes locally
- [ ] `CHANGELOG.md` updated under `[Unreleased]` (user-facing changes)
- [ ] Docs updated (README / `docs/`) if behaviour or setup changed
- [ ] Release PRs only: versions bumped (`scripts/bump-version.sh`) and CHANGELOG section dated
