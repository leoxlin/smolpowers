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
    "phases": {
        "design": {
            "owner": "smolpowers:smol-design",
            "companions": [],
        },
        "plan": {
            "owner": "smolpowers:smol-plan",
            "companions": [],
        },
        "execute": {
            "owner": "smolpowers:smol-execute",
            "companions": [],
            "tdd": "proportional",
        },
        "finish": {
            "owner": "smolpowers:smol-finish",
            "companions": [],
        },
    },
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

mkdir -p "$test_root/json-only"
printf '%s\n' '{"docsRoot":"ignored"}' \
  >"$test_root/json-only/.smolpowers.json"
run_case json-only
assert_json "$(cat "$test_root/json-only/stdout")" \
  "$test_root/json-only/docs/superpowers" "$test_root/json-only/.superpowers"
test ! -s "$test_root/json-only/stderr"

mkdir -p "$test_root/relative"
printf '%s\n' \
  'docsRoot: notes/work' \
  'stateRoot: var/smol' \
  >"$test_root/relative/.smolpowers.yml"
run_case relative
assert_json "$(cat "$test_root/relative/stdout")" \
  "$test_root/relative/notes/work" "$test_root/relative/var/smol"
test ! -s "$test_root/relative/stderr"

mkdir -p "$test_root/preferred"
printf '%s\n' \
  'phases:' \
  '  design:' \
  '    owner: superpowers:brainstorming' \
  '  execute:' \
  '    owner: smolpowers:smol-execute' \
  '    companions:' \
  '      - superpowers:test-driven-development' \
  '    tdd: strict' \
  '  finish:' \
  '    owner: superpowers:finishing-a-development-branch' \
  '    companions: []' \
  >"$test_root/preferred/.smolpowers.yml"
run_case preferred
python3 - "$test_root/preferred/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["phases"]["design"] == {
    "owner": "superpowers:brainstorming",
    "companions": [],
}
assert actual["phases"]["plan"] == {
    "owner": "smolpowers:smol-plan",
    "companions": [],
}
assert actual["phases"]["execute"] == {
    "owner": "smolpowers:smol-execute",
    "companions": ["superpowers:test-driven-development"],
    "tdd": "strict",
}
assert actual["phases"]["finish"] == {
    "owner": "superpowers:finishing-a-development-branch",
    "companions": [],
}
PY
test ! -s "$test_root/preferred/stderr"

mkdir -p "$test_root/preferred-partial"
printf '%s\n' \
  'phases:' \
  '  execute:' \
  '    companions:' \
  '      - superpowers:test-driven-development' \
  >"$test_root/preferred-partial/.smolpowers.yml"
run_case preferred-partial
python3 - "$test_root/preferred-partial/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["phases"]["execute"] == {
    "owner": "smolpowers:smol-execute",
    "companions": ["superpowers:test-driven-development"],
    "tdd": "proportional",
}
PY
test ! -s "$test_root/preferred-partial/stderr"

mkdir -p "$test_root/legacy-owners"
printf '%s\n' \
  'design: superpowers:brainstorming' \
  'finish: superpowers:finishing-a-development-branch' \
  >"$test_root/legacy-owners/.smolpowers.yml"
run_case legacy-owners
python3 - "$test_root/legacy-owners/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["phases"]["design"] == {
    "owner": "superpowers:brainstorming",
    "companions": [],
}
assert actual["phases"]["plan"]["owner"] == "smolpowers:smol-plan"
assert actual["phases"]["execute"]["owner"] == "smolpowers:smol-execute"
assert actual["phases"]["finish"] == {
    "owner": "superpowers:finishing-a-development-branch",
    "companions": [],
}
PY
test ! -s "$test_root/legacy-owners/stderr"

mkdir -p "$test_root/legacy-chain"
printf '%s\n' \
  'execute:' \
  '  - superpowers:test-driven-development' \
  '  - smolpowers:smol-execute' \
  >"$test_root/legacy-chain/.smolpowers.yml"
run_case legacy-chain
python3 - "$test_root/legacy-chain/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["phases"]["execute"] == {
    "owner": "smolpowers:smol-execute",
    "companions": ["superpowers:test-driven-development"],
    "tdd": "proportional",
}
PY
test ! -s "$test_root/legacy-chain/stderr"

mkdir -p "$test_root/legacy-tdd-strict"
printf '%s\n' 'tdd: strict' \
  >"$test_root/legacy-tdd-strict/.smolpowers.yml"
run_case legacy-tdd-strict
python3 - "$test_root/legacy-tdd-strict/stdout" <<'PY'
import json
import sys

with open(sys.argv[1]) as output:
    actual = json.load(output)
assert actual["phases"]["execute"]["tdd"] == "strict"
PY
test ! -s "$test_root/legacy-tdd-strict/stderr"

mkdir -p "$test_root/absolute"
printf '%s\n' \
  'docsRoot: /tmp/smol-docs' \
  'stateRoot: /tmp/smol-state' \
  >"$test_root/absolute/.smolpowers.yml"
run_case absolute
assert_json "$(cat "$test_root/absolute/stdout")" "/tmp/smol-docs" "/tmp/smol-state"

invalid_cases=(
  malformed
  unknown
  atomic
  unsafe
  legacy-invalid-owner
  legacy-empty-chain
  legacy-non-string-member
  legacy-empty-member
  legacy-invalid-tdd
  mixed-shapes
  unknown-phase
  unknown-phase-property
  empty-owner
  non-array-companions
  non-string-companion
  empty-companion
  misplaced-tdd
  invalid-nested-tdd
  phases-scalar
  multiple-documents
)
for name in "${invalid_cases[@]}"; do
  mkdir -p "$test_root/$name"
done

printf '%s\n' 'phases:' '  execute: [unclosed' \
  >"$test_root/malformed/.smolpowers.yml"
printf '%s\n' '{"docsRoot":"docs","surprise":"value"}' \
  >"$test_root/unknown/.smolpowers.yml"
printf '%s\n' '{"docsRoot":"custom","stateRoot":""}' \
  >"$test_root/atomic/.smolpowers.yml"
printf '%s\n' '{"docsRoot":"bad\npath","stateRoot":"custom"}' \
  >"$test_root/unsafe/.smolpowers.yml"
printf '%s\n' '{"design":""}' \
  >"$test_root/legacy-invalid-owner/.smolpowers.yml"
printf '%s\n' '{"execute":[]}' \
  >"$test_root/legacy-empty-chain/.smolpowers.yml"
printf '%s\n' '{"execute":["smolpowers:smol-execute",42]}' \
  >"$test_root/legacy-non-string-member/.smolpowers.yml"
printf '%s\n' '{"execute":["","smolpowers:smol-execute"]}' \
  >"$test_root/legacy-empty-member/.smolpowers.yml"
printf '%s\n' '{"tdd":"sometimes"}' \
  >"$test_root/legacy-invalid-tdd/.smolpowers.yml"
printf '%s\n' '{"execute":"smolpowers:smol-execute","phases":{}}' \
  >"$test_root/mixed-shapes/.smolpowers.yml"
printf '%s\n' '{"phases":{"deploy":{"owner":"example:deploy"}}}' \
  >"$test_root/unknown-phase/.smolpowers.yml"
printf '%s\n' '{"phases":{"design":{"mode":"fast"}}}' \
  >"$test_root/unknown-phase-property/.smolpowers.yml"
printf '%s\n' '{"phases":{"design":{"owner":""}}}' \
  >"$test_root/empty-owner/.smolpowers.yml"
printf '%s\n' '{"phases":{"execute":{"companions":"example:tdd"}}}' \
  >"$test_root/non-array-companions/.smolpowers.yml"
printf '%s\n' '{"phases":{"execute":{"companions":[42]}}}' \
  >"$test_root/non-string-companion/.smolpowers.yml"
printf '%s\n' '{"phases":{"execute":{"companions":[""]}}}' \
  >"$test_root/empty-companion/.smolpowers.yml"
printf '%s\n' '{"phases":{"design":{"tdd":"strict"}}}' \
  >"$test_root/misplaced-tdd/.smolpowers.yml"
printf '%s\n' '{"phases":{"execute":{"tdd":"sometimes"}}}' \
  >"$test_root/invalid-nested-tdd/.smolpowers.yml"
printf '%s\n' 'phases: execute' \
  >"$test_root/phases-scalar/.smolpowers.yml"
printf '%s\n' \
  'docsRoot: first' \
  '---' \
  'docsRoot: second' \
  >"$test_root/multiple-documents/.smolpowers.yml"

for name in "${invalid_cases[@]}"; do
  run_case "$name"
  assert_json "$(cat "$test_root/$name/stdout")" \
    "$test_root/$name/docs/superpowers" "$test_root/$name/.superpowers"
  test "$(wc -l <"$test_root/$name/stderr" | tr -d ' ')" = "1"
done

mkdir -p "$test_root/no-yq"
printf '%s\n' \
  'docsRoot: custom' \
  'stateRoot: state' \
  >"$test_root/no-yq/.smolpowers.yml"
PATH=/nonexistent /bin/bash "$loader" "$test_root/no-yq" \
  >"$test_root/no-yq/stdout" 2>"$test_root/no-yq/stderr"
assert_json "$(cat "$test_root/no-yq/stdout")" \
  "$test_root/no-yq/docs/superpowers" "$test_root/no-yq/.superpowers"
test "$(wc -l <"$test_root/no-yq/stderr" | tr -d ' ')" = "1"

printf '%s\n' "Configuration loader tests passed"
