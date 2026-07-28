#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
exec uv run --project "$repo_root/tests" --locked \
  pytest -c "$repo_root/tests/pyproject.toml" "$@"
