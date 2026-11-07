#!/usr/bin/env bash
# Verify that backend, frontend and CHANGELOG agree on a release version.
#   usage: scripts/check-version.sh 1.2.3
set -euo pipefail

expected="${1:?usage: $0 X.Y.Z}"
root="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! "$expected" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "::error::'$expected' is not a valid X.Y.Z version" >&2
  exit 1
fi

backend="$(sed -nE 's/^version = "([^"]+)"/\1/p' "$root/backend/pyproject.toml" | head -n1)"
frontend="$(sed -nE 's/^  "version": "([^"]+)",?/\1/p' "$root/frontend/package.json" | head -n1)"
status=0

check() {
  if [[ "$2" == "$expected" ]]; then
    echo "✅ $1: $2"
  else
    echo "::error title=Version mismatch::$1 is '$2', expected '$expected'"
    status=1
  fi
}

check "backend/pyproject.toml" "$backend"
check "frontend/package.json" "$frontend"

if grep -qE "^## \[$expected\]" "$root/CHANGELOG.md"; then
  echo "✅ CHANGELOG.md has a [$expected] section"
else
  echo "::error title=Missing changelog::CHANGELOG.md has no '## [$expected]' section"
  status=1
fi

exit "$status"
