#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
output="$(CLAUDE_PLUGIN_ROOT="$repo_root" bash "$repo_root/hooks/session-start")"

python3 - "$output" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
assert set(payload) == {"hookSpecificOutput"}
hook = payload["hookSpecificOutput"]
assert hook["hookEventName"] == "SessionStart"
context = hook["additionalContext"]
assert "smolpowers:smol-activate bootstrap" in context
assert "Plan" in context and "Design" in context
assert "TODO" not in context
PY

wrapper_output="$(
  CLAUDE_PLUGIN_ROOT="$repo_root" bash "$repo_root/hooks/run-hook.cmd" session-start
)"
test "$wrapper_output" = "$output"

printf '%s\n' "Claude SessionStart bootstrap tests passed"
