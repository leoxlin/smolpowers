#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=tests/integration-test-lib.sh
source "$repo_root/tests/integration-test-lib.sh"
discovery_only=false

case "${1:-}" in
  "") ;;
  --discovery-only) discovery_only=true ;;
  *)
    printf 'usage: %s [--discovery-only]\n' "$0" >&2
    exit 2
    ;;
esac

test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

fail() {
  local agent="$1"
  local message="$2"
  local transcript="$test_root/$agent/codex.log"
  local install_log="$test_root/$agent/install.log"

  printf 'Configuration override integration test failed [%s]: %s\n' \
    "$agent" "$message" >&2
  if [[ -s "$transcript" ]]; then
    printf '%s\n' '--- Agent transcript ---' >&2
    sed -n '1,400p' "$transcript" >&2
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
  transcript="$agent_root/codex.log"
  install_log="$agent_root/install.log"
  last_message="$agent_root/last-message.txt"

  mkdir -p "$fixture"
  git -C "$fixture" init -q

  printf '%s\n' \
    'docsRoot: artifacts' \
    'stateRoot: .smol-state' \
    'phases:' \
    '  design:' \
    '    owner: integration-design' \
    '  plan:' \
    '    owner: integration-plan' \
    '  execute:' \
    '    owner: integration-execute' \
    '  finish:' \
    '    owner: integration-finish' \
    >"$fixture/.smolpowers.yml"
  printf '# Configuration override fixture\n' >"$fixture/README.md"

  integration_install_skills \
    "$fixture" "$agent" "$repo_root" '*' \
    >"$install_log" 2>&1 \
    || fail "$agent" "could not install all Smolpowers skills with npx skills"
  integration_install_skills \
    "$fixture" "$agent" "$repo_root/tests/fixtures/override-skills" '*' \
    >>"$install_log" 2>&1 \
    || fail "$agent" "could not install the recorder-owner skills with npx skills"
  integration_assert_skills \
    "$fixture" "$agent" \
    smol-activate smol-design smol-plan smol-execute smol-finish \
    integration-design integration-plan integration-execute integration-finish \
    || fail "$agent" "installed skill inventory is incomplete"

  git -C "$fixture" add .
  git -C "$fixture" \
    -c user.name='Smolpowers Integration' \
    -c user.email='integration@example.invalid' \
    commit -qm 'test: initialize override fixture'

  if [[ "$discovery_only" == true ]]; then
    printf 'Configuration override discovery passed [%s]\n' "$agent"
    continue
  fi

  integration_require_agent "$agent" \
    || fail "$agent" "agent executable is unavailable"

  # shellcheck disable=SC2016
  prompt='Use $smol-activate to create result.txt containing exactly `override lifecycle passed` plus a newline. Continue automatically through Finish using every configured phase owner and configured root. Do not commit.'

  integration_run_agent \
    "$fixture" "$agent" "$prompt" "$transcript" "$last_message" \
    || fail "$agent" "agent exited nonzero"

  docs_root="$fixture/artifacts"
  state_root="$fixture/.smol-state"
  calls="$state_root/phase-calls.log"
  expected="$agent_root/expected-calls.log"

  printf 'design|%s|%s\nplan|%s|%s\nexecute|%s|%s\nfinish|%s|%s\n' \
    "$docs_root" "$state_root" \
    "$docs_root" "$state_root" \
    "$docs_root" "$state_root" \
    "$docs_root" "$state_root" >"$expected"

  [[ -f "$calls" ]] || fail "$agent" "configured stateRoot call log is missing"
  diff -u "$expected" "$calls" \
    || fail "$agent" "configured owners were not called in order"
  [[ -f "$fixture/result.txt" ]] \
    || fail "$agent" "fixture result.txt is missing"
  [[ "$(<"$fixture/result.txt")" == 'override lifecycle passed' ]] \
    || fail "$agent" "fixture result.txt has unexpected content"
  [[ -d "$docs_root/specs" ]] \
    || fail "$agent" "configured docsRoot specs directory is missing"
  [[ -d "$docs_root/plans" ]] \
    || fail "$agent" "configured docsRoot plans directory is missing"
  [[ "$(find "$docs_root/specs" -type f \
    -name '*-override-lifecycle-design.md' | wc -l | tr -d ' ')" == 1 ]] \
    || fail "$agent" "configured docsRoot does not contain exactly one matching spec"
  [[ "$(find "$docs_root/plans" -type f \
    -name '*-override-lifecycle.md' | wc -l | tr -d ' ')" == 1 ]] \
    || fail "$agent" "configured docsRoot does not contain exactly one matching plan"
  grep -R -Fq 'Status: Current' "$docs_root/specs" \
    || fail "$agent" "integration spec is not current"
  ! grep -R -q -- '- \[ \]' "$docs_root/plans" \
    || fail "$agent" "integration plan still has unchecked tasks"
  [[ ! -e "$fixture/docs/superpowers" ]] \
    || fail "$agent" "default docsRoot was created"
  [[ ! -e "$fixture/.superpowers" ]] \
    || fail "$agent" "default stateRoot was created"

  printf 'Configuration override integration test passed [%s]\n' "$agent"
done
