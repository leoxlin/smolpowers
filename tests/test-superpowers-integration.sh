#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
codex_bin="${CODEX_BIN:-codex}"
upstream_root="${SUPERPOWERS_ROOT:-$repo_root/../superpowers}"
host_codex_home="${CODEX_HOME:-$HOME/.codex}"
discovery_only=false

case "${1:-}" in
  "") ;;
  --discovery-only) discovery_only=true ;;
  *)
    printf 'usage: %s [--discovery-only]\n' "$0" >&2
    exit 2
    ;;
esac

command -v "$codex_bin" >/dev/null 2>&1 || {
  printf 'SKIP: CODEX_BIN is not executable: %s\n' "$codex_bin"
  exit 0
}
for skill in writing-plans test-driven-development; do
  [[ -f "$upstream_root/skills/$skill/SKILL.md" ]] || {
    printf 'SKIP: SUPERPOWERS_ROOT lacks skills/%s/SKILL.md\n' "$skill"
    exit 0
  }
done
if [[ "$discovery_only" == false \
  && ! -f "$host_codex_home/auth.json" \
  && -z "${OPENAI_API_KEY:-}" ]]; then
  printf 'SKIP: Codex authentication is unavailable\n'
  exit 0
fi

mkdir -p "$repo_root/.superpowers"
test_root="$(mktemp -d "$repo_root/.superpowers/integration.XXXXXX")"
fixture="$test_root/repo"
marketplace="$test_root/superpowers-fixture"
test_codex_home="$test_root/codex-home"
transcript="$test_root/codex.log"
plugin_list="$test_root/plugins.json"
prompt_input="$test_root/prompt-input.json"
last_message="$test_root/last-message.txt"
verifier="$test_root/verify-finished.sh"
trap 'rm -rf "$test_root"' EXIT

fail() {
  printf 'Selected Superpowers integration test failed: %s\n' "$1" >&2
  if [[ -s "$transcript" ]]; then
    printf '%s\n' '--- Codex transcript ---' >&2
    tail -n 400 "$transcript" >&2
  elif [[ -s "$last_message" ]]; then
    printf '%s\n' '--- Codex final response ---' >&2
    sed -n '1,200p' "$last_message" >&2
  elif [[ -f "$prompt_input" ]]; then
    printf '%s\n' '--- Codex prompt input ---' >&2
    sed -n '1,240p' "$prompt_input" >&2
  fi
  exit 1
}

mkdir -p \
  "$marketplace/.agents/plugins" \
  "$marketplace/plugins/superpowers/.codex-plugin" \
  "$marketplace/plugins/superpowers/skills" \
  "$test_codex_home" \
  "$fixture/tests"
cp -R \
  "$upstream_root/skills/writing-plans" \
  "$upstream_root/skills/test-driven-development" \
  "$marketplace/plugins/superpowers/skills/"

printf '%s\n' \
  '{' \
  '  "name": "superpowers-fixture",' \
  '  "interface": {"displayName": "Selected Superpowers Fixture"},' \
  '  "plugins": [' \
  '    {' \
  '      "name": "superpowers",' \
  '      "source": {"source": "url", "url": "./plugins/superpowers"},' \
  '      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},' \
  '      "category": "Developer Tools"' \
  '    }' \
  '  ]' \
  '}' >"$marketplace/.agents/plugins/marketplace.json"

printf '%s\n' \
  '{' \
  '  "name": "superpowers",' \
  '  "version": "0.0.0-integration",' \
  '  "description": "Selected real Superpowers skills for integration testing.",' \
  '  "author": {"name": "Jesse Vincent"},' \
  '  "license": "MIT",' \
  '  "keywords": ["planning", "tdd"],' \
  '  "skills": "./skills/",' \
  '  "hooks": {},' \
  '  "interface": {' \
  '    "displayName": "Selected Superpowers",' \
  '    "shortDescription": "Selected upstream workflow skills",' \
  '    "longDescription": "Real upstream Plan and TDD skills for mixed lifecycle testing.",' \
  '    "developerName": "Jesse Vincent",' \
  '    "category": "Developer Tools",' \
  '    "capabilities": ["Read", "Write"]' \
  '  }' \
  '}' >"$marketplace/plugins/superpowers/.codex-plugin/plugin.json"

git -C "$marketplace/plugins/superpowers" init -q
git -C "$marketplace/plugins/superpowers" add .
git -C "$marketplace/plugins/superpowers" \
  -c user.name='Smolpowers Integration' \
  -c user.email='integration@example.invalid' \
  commit -qm 'test: package selected Superpowers skills'

if [[ -f "$host_codex_home/auth.json" ]]; then
  ln -s "$host_codex_home/auth.json" "$test_codex_home/auth.json"
fi

CODEX_HOME="$test_codex_home" "$codex_bin" plugin marketplace add \
  "$repo_root" --json >/dev/null \
  || fail "could not add the Smolpowers marketplace"
CODEX_HOME="$test_codex_home" "$codex_bin" plugin marketplace add \
  "$marketplace" --json >/dev/null \
  || fail "could not add the selected Superpowers marketplace"
CODEX_HOME="$test_codex_home" "$codex_bin" plugin add \
  smolpowers@smolpowers --json >/dev/null \
  || fail "could not install Smolpowers"
CODEX_HOME="$test_codex_home" "$codex_bin" plugin add \
  superpowers@superpowers-fixture --json >/dev/null \
  || fail "could not install selected Superpowers skills"
CODEX_HOME="$test_codex_home" "$codex_bin" plugin list --json >"$plugin_list" \
  || fail "could not list installed plugins"

python3 - "$plugin_list" <<'PY' || fail "expected plugins are not installed and enabled"
import json
import sys

with open(sys.argv[1]) as source:
    plugins = {item["pluginId"]: item for item in json.load(source)["installed"]}
for plugin_id in ("smolpowers@smolpowers", "superpowers@superpowers-fixture"):
    assert plugins[plugin_id]["enabled"] is True
PY

printf '%s\n' \
  'docsRoot: artifacts' \
  'stateRoot: .smol-state' \
  'phases:' \
  '  design:' \
  '    owner: smolpowers:smol-design' \
  '  plan:' \
  '    owner: superpowers:writing-plans' \
  '  execute:' \
  '    owner: smolpowers:smol-execute' \
  '    companions:' \
  '      - superpowers:test-driven-development' \
  '  finish:' \
  '    owner: smolpowers:smol-finish' \
  >"$fixture/.smolpowers.yml"
printf '%s\n' '# Mixed Smolpowers and Superpowers fixture' >"$fixture/README.md"
# shellcheck disable=SC2016
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  'actual="$(bin/greet.sh)"' \
  '[[ "$actual" == "hello from mixed skills" ]]' \
  >"$fixture/tests/test-greet.sh"
chmod +x "$fixture/tests/test-greet.sh"

cat >"$verifier" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

fixture="${1:?fixture path is required}"
spec="$(find "$fixture/artifacts/specs" -type f \
  -name '*-mixed-superpowers-design.md' -print -quit)"
plan="$(find "$fixture/artifacts/plans" -type f \
  -name '*-mixed-superpowers.md' -print -quit)"

[[ -x "$fixture/bin/greet.sh" ]]
bash "$fixture/tests/test-greet.sh"
[[ -f "$spec" ]]
[[ -f "$plan" ]]
grep -Fq '**Status:** Current' "$spec"
grep -Fq '> **For agentic workers:** REQUIRED SUB-SKILL:' "$plan"
! grep -q -- '- \[ \]' "$plan"
git -C "$fixture" diff --quiet -- .smolpowers.yml tests/test-greet.sh
git -C "$fixture" diff --check
printf '%s\n' 'MIXED_SUPERPOWERS_VERIFIED'
SH
chmod 555 "$verifier"

git -C "$fixture" init -q
git -C "$fixture" add .
git -C "$fixture" \
  -c user.name='Smolpowers Integration' \
  -c user.email='integration@example.invalid' \
  commit -qm 'test: initialize mixed-skill fixture'

# shellcheck disable=SC2016
prompt='Use $smolpowers:smol-activate with $superpowers:writing-plans as the configured Plan owner and $superpowers:test-driven-development as the configured Execute companion. Use the artifact slug `mixed-superpowers` to make the existing `tests/test-greet.sh` pass by adding the minimum production code, then continue automatically through Finish. Preserve the existing test and configuration. During Finish, run `bash '"$verifier"' .` and do not repeat its sentinel in your final response. Do not ask questions, commit, or push. In your final response, name each configured upstream skill you actually invoked.'

if ! (
  cd "$fixture"
  CODEX_HOME="$test_codex_home" "$codex_bin" debug prompt-input "$prompt"
) >"$prompt_input" 2>/dev/null; then
  fail "Codex could not render the installed skills"
fi
grep -Fq 'smolpowers:smol-activate' "$prompt_input" \
  || fail "Codex did not discover the Smolpowers bootstrap"
grep -Fq 'superpowers:writing-plans' "$prompt_input" \
  || fail "Codex did not discover the upstream Plan owner"
grep -Fq 'superpowers:test-driven-development' "$prompt_input" \
  || fail "Codex did not discover the upstream TDD companion"

if [[ "$discovery_only" == true ]]; then
  printf '%s\n' "Selected Superpowers discovery test passed"
  exit 0
fi

if ! CODEX_HOME="$test_codex_home" "$codex_bin" exec \
  --color never \
  --sandbox workspace-write \
  --output-last-message "$last_message" \
  -C "$fixture" \
  "$prompt" </dev/null >"$transcript" 2>&1; then
  fail "Codex exited nonzero"
fi

grep -Fxq 'MIXED_SUPERPOWERS_VERIFIED' "$transcript" \
  || fail "the in-session Finish verifier did not pass"
grep -Fq 'No such file or directory' "$transcript" \
  || fail "the transcript does not contain the expected failing test run"
grep -Fq 'superpowers:writing-plans' "$last_message" \
  || fail "the final response omits the upstream Plan owner"
grep -Fq 'superpowers:test-driven-development' "$last_message" \
  || fail "the final response omits the upstream TDD companion"

printf '%s\n' "Selected Superpowers integration test passed"
