#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
exec uv run --project "$repo_root" --locked \
  pytest -c "$repo_root/pyproject.toml" "$@"
