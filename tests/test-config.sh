#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
loader="$repo_root/skills/smol-activate/scripts/load-config.sh"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

assert_json() {
  local output="$1"
  local docs="$2"
  local state="$3"
  python3 - "$output" "$docs" "$state" <<'PY'
import json
import sys

actual = json.loads(sys.argv[1])
expected = {
    "docsRoot": sys.argv[2],
    "stateRoot": sys.argv[3],
    "design": "smolpowers:smol-design",
    "plan": "smolpowers:smol-plan",
    "execute": "smolpowers:smol-execute",
    "finish": "smolpowers:smol-finish",
}
assert actual == expected, f"expected {expected!r}, got {actual!r}"
PY
}

run_case() {
  local name="$1"
  local fixture="$test_root/$name"
  mkdir -p "$fixture"
  stdout_file="$fixture/stdout"
  stderr_file="$fixture/stderr"
  /bin/bash "$loader" "$fixture" >"$stdout_file" 2>"$stderr_file"
}

run_case absent
assert_json "$(cat "$test_root/absent/stdout")" \
  "$test_root/absent/docs/superpowers" "$test_root/absent/.superpowers"
test ! -s "$test_root/absent/stderr"

mkdir -p "$test_root/relative"
printf '%s\n' '{"docsRoot":"notes/work","stateRoot":"var/smol"}' \
  >"$test_root/relative/.smolpowers.json"
run_case relative
assert_json "$(cat "$test_root/relative/stdout")" \
  "$test_root/relative/notes/work" "$test_root/relative/var/smol"
test ! -s "$test_root/relative/stderr"

mkdir -p "$test_root/phases"
printf '%s\n' \
  '{"design":"superpowers:brainstorming","finish":"superpowers:finishing-a-development-branch"}' \
  >"$test_root/phases/.smolpowers.json"
run_case phases
python3 - "$test_root/phases/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["design"] == "superpowers:brainstorming"
assert actual["plan"] == "smolpowers:smol-plan"
assert actual["execute"] == "smolpowers:smol-execute"
assert actual["finish"] == "superpowers:finishing-a-development-branch"
PY
test ! -s "$test_root/phases/stderr"

mkdir -p "$test_root/phase-chain"
printf '%s\n' \
  '{"execute":["superpowers:test-driven-development","smolpowers:smol-execute"]}' \
  >"$test_root/phase-chain/.smolpowers.json"
run_case phase-chain
python3 - "$test_root/phase-chain/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["design"] == "smolpowers:smol-design"
assert actual["plan"] == "smolpowers:smol-plan"
assert actual["execute"] == [
    "superpowers:test-driven-development",
    "smolpowers:smol-execute",
]
assert actual["finish"] == "smolpowers:smol-finish"
PY
test ! -s "$test_root/phase-chain/stderr"

mkdir -p "$test_root/absolute"
printf '%s\n' '{"docsRoot":"/tmp/smol-docs","stateRoot":"/tmp/smol-state"}' \
  >"$test_root/absolute/.smolpowers.json"
run_case absolute
assert_json "$(cat "$test_root/absolute/stdout")" "/tmp/smol-docs" "/tmp/smol-state"

for name in malformed unknown atomic unsafe invalid-skill \
  empty-phase-chain non-string-phase-member empty-phase-member; do
  mkdir -p "$test_root/$name"
done
printf '%s\n' '{not json' >"$test_root/malformed/.smolpowers.json"
printf '%s\n' '{"docsRoot":"docs","surprise":"value"}' \
  >"$test_root/unknown/.smolpowers.json"
printf '%s\n' '{"docsRoot":"custom","stateRoot":""}' \
  >"$test_root/atomic/.smolpowers.json"
printf '%s\n' '{"docsRoot":"bad\npath","stateRoot":"custom"}' \
  >"$test_root/unsafe/.smolpowers.json"
printf '%s\n' '{"design":""}' >"$test_root/invalid-skill/.smolpowers.json"
printf '%s\n' '{"execute":[]}' \
  >"$test_root/empty-phase-chain/.smolpowers.json"
printf '%s\n' '{"execute":["smolpowers:smol-execute",42]}' \
  >"$test_root/non-string-phase-member/.smolpowers.json"
printf '%s\n' '{"execute":["","smolpowers:smol-execute"]}' \
  >"$test_root/empty-phase-member/.smolpowers.json"

for name in malformed unknown atomic unsafe invalid-skill \
  empty-phase-chain non-string-phase-member empty-phase-member; do
  run_case "$name"
  assert_json "$(cat "$test_root/$name/stdout")" \
    "$test_root/$name/docs/superpowers" "$test_root/$name/.superpowers"
  test "$(wc -l <"$test_root/$name/stderr" | tr -d ' ')" = "1"
done

mkdir -p "$test_root/no-jq"
printf '%s\n' '{"docsRoot":"custom","stateRoot":"state"}' \
  >"$test_root/no-jq/.smolpowers.json"
PATH=/nonexistent /bin/bash "$loader" "$test_root/no-jq" \
  >"$test_root/no-jq/stdout" 2>"$test_root/no-jq/stderr"
assert_json "$(cat "$test_root/no-jq/stdout")" \
  "$test_root/no-jq/docs/superpowers" "$test_root/no-jq/.superpowers"
test "$(wc -l <"$test_root/no-jq/stderr" | tr -d ' ')" = "1"

printf '%s\n' "Configuration loader tests passed"
