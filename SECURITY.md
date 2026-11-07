# Security Policy

## Supported versions

Only the latest release (`:latest` / newest `vX.Y.Z`) receives security fixes, shipped as a
[hotfix](docs/GIT_FLOW.md#7-hotfix-urgent-production-fix).

## Reporting a vulnerability

Do **not** open a public issue. Report it privately via
[GitHub Security Advisories](https://github.com/messeb/python-hackathon-setup/security/advisories/new).
You will get an acknowledgement within 3 working days.

## Supply-chain measures

- GitHub Actions pinned to full commit SHAs, updated weekly by Dependabot.
- Release images built from scratch (no cache), with SBOM, SLSA provenance and a signed
  attestation: `gh attestation verify oci://ghcr.io/messeb/python-hackathon-setup:<version> -R messeb/python-hackathon-setup`.
- CodeQL (`security-extended`), dependency review on PRs, actionlint + zizmor on workflows.
- Container runs as non-root (UID 10001); compose example uses a read-only root filesystem.
- Secrets only via environment variables (`APP_*`), never committed (`.env` is git-ignored).
