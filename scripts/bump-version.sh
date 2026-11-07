#!/usr/bin/env bash
# Set the application version everywhere it lives (backend, frontend, uv.lock).
#   usage: scripts/bump-version.sh 1.2.3
set -euo pipefail

version="${1:?usage: $0 X.Y.Z}"
root="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "error: '$version' is not X.Y.Z (RC suffixes live on git tags only)" >&2
  exit 1
fi

(cd "$root/backend" && uv version "$version" --quiet)
(cd "$root/frontend" && npm pkg set version="$version")

echo "Version set to $version:"
"$root/scripts/check-version.sh" "$version" || true
