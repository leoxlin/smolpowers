#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=tests/integration-test-lib.sh
source "$repo_root/tests/integration-test-lib.sh"
upstream_root="${SUPERPOWERS_ROOT:-$repo_root/../superpowers}"
discovery_only=false

case "${1:-}" in
  "") ;;
  --discovery-only) discovery_only=true ;;
  *)
    printf 'usage: %s [--discovery-only]\n' "$0" >&2
    exit 2
    ;;
esac

for skill in writing-plans test-driven-development; do
  [[ -f "$upstream_root/skills/$skill/SKILL.md" ]] || {
    printf 'SKIP: SUPERPOWERS_ROOT lacks skills/%s/SKILL.md\n' "$skill"
    exit 0
  }
done

test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

fail() {
  local agent="$1"
  local message="$2"
  local transcript="$test_root/$agent/agent.log"
  local last_message="$test_root/$agent/last-message.txt"
  local install_log="$test_root/$agent/install.log"

  printf 'Selected Superpowers integration test failed [%s]: %s\n' \
    "$agent" "$message" >&2
  if [[ -s "$transcript" ]]; then
    printf '%s\n' '--- Agent transcript ---' >&2
    tail -n 400 "$transcript" >&2
  elif [[ -s "$last_message" ]]; then
    printf '%s\n' '--- Agent final response ---' >&2
    sed -n '1,200p' "$last_message" >&2
  elif [[ -s "$install_log" ]]; then
    printf '%s\n' '--- Skill installation log ---' >&2
    sed -n '1,400p' "$install_log" >&2
  fi
  exit 1
}

agent_types="$(integration_agent_types)"
# shellcheck disable=SC2086
for agent in $agent_types; do
  agent_root="$test_root/$agent"
  fixture="$agent_root/repo"
  transcript="$agent_root/agent.log"
  install_log="$agent_root/install.log"
  last_message="$agent_root/last-message.txt"
  verifier="$agent_root/verify-finished.sh"

  mkdir -p "$fixture/tests"
  git -C "$fixture" init -q

  printf '%s\n' \
    'docsRoot: artifacts' \
    'stateRoot: .smol-state' \
    'phases:' \
    '  design:' \
    '    owner: smol-design' \
    '  plan:' \
    '    owner: writing-plans' \
    '  execute:' \
    '    owner: smol-execute' \
    '    companions:' \
    '      - test-driven-development' \
    '  finish:' \
    '    owner: smol-finish' \
    >"$fixture/.smolpowers.yml"
  printf '%s\n' '# Mixed Smolpowers and Superpowers fixture' \
    >"$fixture/README.md"
  # shellcheck disable=SC2016
  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'set -euo pipefail' \
    'actual="$(bin/greet.sh)"' \
    '[[ "$actual" == "hello from mixed skills" ]]' \
    >"$fixture/tests/test-greet.sh"
  chmod +x "$fixture/tests/test-greet.sh"

  # shellcheck disable=SC2016
  printf '%s\n' \
    '#!/usr/bin/env bash' \
    'set -euo pipefail' \
    '' \
    'fixture="${1:?fixture path is required}"' \
    'spec="$(find "$fixture/artifacts/specs" -type f -name '"'"'*-mixed-superpowers-design.md'"'"' -print -quit)"' \
    'plan="$(find "$fixture/artifacts/plans" -type f -name '"'"'*-mixed-superpowers.md'"'"' -print -quit)"' \
    '' \
    '[[ -x "$fixture/bin/greet.sh" ]]' \
    'bash "$fixture/tests/test-greet.sh"' \
    '[[ -f "$spec" ]]' \
    '[[ -f "$plan" ]]' \
    'grep -Fq '"'"'**Status:** Current'"'"' "$spec"' \
    'grep -Fq '"'"'> **For agentic workers:** REQUIRED SUB-SKILL:'"'"' "$plan"' \
    '! grep -q -- '"'"'- \[ \]'"'"' "$plan"' \
    'git -C "$fixture" diff --quiet -- .smolpowers.yml tests/test-greet.sh' \
    'git -C "$fixture" diff --check' \
    'printf '"'"'%s\n'"'"' '"'"'MIXED_SUPERPOWERS_VERIFIED'"'"'' \
    >"$verifier"
  chmod 555 "$verifier"

  integration_install_skills \
    "$fixture" "$agent" "$repo_root" '*' \
    >"$install_log" 2>&1 \
    || fail "$agent" "could not install all Smolpowers skills with npx skills"
  integration_install_skills \
    "$fixture" "$agent" "$upstream_root" \
    writing-plans test-driven-development \
    >>"$install_log" 2>&1 \
    || fail "$agent" "could not install selected Superpowers skills with npx skills"
  integration_assert_skills \
    "$fixture" "$agent" \
    smol-activate smol-design smol-plan smol-execute smol-finish \
    writing-plans test-driven-development \
    || fail "$agent" "installed skill inventory is incomplete"

  git -C "$fixture" add .
  git -C "$fixture" \
    -c user.name='Smolpowers Integration' \
    -c user.email='integration@example.invalid' \
    commit -qm 'test: initialize mixed-skill fixture'

  if [[ "$discovery_only" == true ]]; then
    printf 'Selected Superpowers discovery passed [%s]\n' "$agent"
    continue
  fi

  integration_require_agent "$agent" \
    || fail "$agent" "agent executable is unavailable"

  # shellcheck disable=SC2016
  prompt='Use $smol-activate with $writing-plans as the configured Plan owner and $test-driven-development as the configured Execute companion. Use the artifact slug `mixed-superpowers` to make the existing `tests/test-greet.sh` pass by adding the minimum production code, then continue automatically through Finish. Preserve the existing test, installed skills, and configuration. During Finish, run `bash '"$verifier"' .` and do not repeat its sentinel in your final response. Do not ask questions, commit, or push. In your final response, name each configured upstream skill you actually invoked.'

  integration_run_agent \
    "$fixture" "$agent" "$prompt" "$transcript" "$last_message" \
    || fail "$agent" "agent exited nonzero"

  grep -Fq 'MIXED_SUPERPOWERS_VERIFIED' "$transcript" \
    || fail "$agent" "the in-session Finish verifier did not pass"
  grep -Fq 'No such file or directory' "$transcript" \
    || fail "$agent" "the transcript does not contain the expected failing test run"
  grep -Fq 'writing-plans' "$transcript" \
    || fail "$agent" "the transcript omits the upstream Plan owner call"
  grep -Fq 'test-driven-development' "$transcript" \
    || fail "$agent" "the transcript omits the upstream TDD companion call"

  printf 'Selected Superpowers integration test passed [%s]\n' "$agent"
done
