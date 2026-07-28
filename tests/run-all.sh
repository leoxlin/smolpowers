#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

python3 tests/test-skills.py
bash tests/test-config.sh
python3 tests/test-manifests.py
bash tests/test-session-start.sh
node --test tests/test-pi.mjs
python3 tests/test-artifacts.py
bash tests/test-upstream.sh

bash -n hooks/session-start hooks/run-hook.cmd \
  skills/smol-activate/scripts/load-config.sh tests/*.sh

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck hooks/session-start skills/smol-activate/scripts/load-config.sh tests/*.sh
else
  printf '%s\n' "SKIP: shellcheck is not installed"
fi

printf '%s\n' "All focused tests passed"
