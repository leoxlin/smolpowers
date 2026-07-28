#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
codex_bin="${CODEX_BIN:-codex}"
test_root="$(mktemp -d)"
fixture="$test_root/repo"
transcript="$test_root/codex.log"
trap 'rm -rf "$test_root"' EXIT

fail() {
  printf 'Configuration override integration test failed: %s\n' "$1" >&2
  if [[ -f "$transcript" ]]; then
    printf '%s\n' '--- Codex transcript ---' >&2
    sed -n '1,400p' "$transcript" >&2
  fi
  exit 1
}

command -v "$codex_bin" >/dev/null 2>&1 \
  || fail "CODEX_BIN is not executable: $codex_bin"

mkdir -p "$fixture/.agents/skills"
cp -R "$repo_root/skills/smol-activate" "$fixture/.agents/skills/"
cp -R "$repo_root/tests/fixtures/override-skills/." "$fixture/.agents/skills/"

printf '%s\n' \
  '{"docsRoot":"artifacts","stateRoot":".smol-state","design":"integration-design","plan":"integration-plan","execute":"integration-execute","finish":"integration-finish"}' \
  >"$fixture/.smolpowers.json"
printf '# Configuration override fixture\n' >"$fixture/README.md"

git -C "$fixture" init -q
git -C "$fixture" add .
git -C "$fixture" \
  -c user.name='Smolpowers Integration' \
  -c user.email='integration@example.invalid' \
  commit -qm 'test: initialize override fixture'

# shellcheck disable=SC2016
prompt='Use $smol-activate to create result.txt containing exactly `override lifecycle passed` plus a newline. Continue automatically through Finish using every configured phase owner and configured root. Do not commit.'

if ! "$codex_bin" exec \
  --ephemeral \
  --color never \
  --sandbox workspace-write \
  -C "$fixture" \
  "$prompt" </dev/null >"$transcript" 2>&1; then
  fail "Codex exited nonzero"
fi

docs_root="$fixture/artifacts"
state_root="$fixture/.smol-state"
calls="$state_root/phase-calls.log"
expected="$test_root/expected-calls.log"

printf 'design|%s|%s\nplan|%s|%s\nexecute|%s|%s\nfinish|%s|%s\n' \
  "$docs_root" "$state_root" \
  "$docs_root" "$state_root" \
  "$docs_root" "$state_root" \
  "$docs_root" "$state_root" >"$expected"

[[ -f "$calls" ]] || fail "configured stateRoot call log is missing"
diff -u "$expected" "$calls" || fail "configured owners were not called in order"
[[ -f "$fixture/result.txt" ]] || fail "fixture result.txt is missing"
[[ "$(<"$fixture/result.txt")" == 'override lifecycle passed' ]] \
  || fail "fixture result.txt has unexpected content"
[[ -d "$docs_root/specs" ]] || fail "configured docsRoot specs directory is missing"
[[ -d "$docs_root/plans" ]] || fail "configured docsRoot plans directory is missing"
[[ "$(find "$docs_root/specs" -type f -name '*-override-lifecycle-design.md' | wc -l | tr -d ' ')" == 1 ]] \
  || fail "configured docsRoot does not contain exactly one matching spec"
[[ "$(find "$docs_root/plans" -type f -name '*-override-lifecycle.md' | wc -l | tr -d ' ')" == 1 ]] \
  || fail "configured docsRoot does not contain exactly one matching plan"
! grep -R -q -- '- \[ \]' "$docs_root/plans" \
  || fail "integration plan still has unchecked tasks"
[[ ! -e "$fixture/docs/superpowers" ]] || fail "default docsRoot was created"
[[ ! -e "$fixture/.superpowers" ]] || fail "default stateRoot was created"

printf '%s\n' "Configuration override integration test passed"
