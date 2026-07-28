#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
upstream_root="${SUPERPOWERS_ROOT:-$repo_root/../superpowers}"
compatibility="$repo_root/skills/smol-activate/references/compatibility.md"

for token in workflow_owner output_path tracked_artifact return_to_caller; do
  grep -q "$token" "$compatibility"
done
# shellcheck disable=SC2016
grep -Fq '| `superpowers:subagent-driven-development` | Execute |' "$compatibility"
# shellcheck disable=SC2016
grep -Fq '| `superpowers:executing-plans` | Execute and Finish |' "$compatibility"
grep -Fq 'superpowers:test-driven-development' "$compatibility"
grep -Fq 'companion' "$compatibility"

for skill in smol-activate smol-design smol-plan smol-execute smol-finish; do
  grep -Fq 'phase chain' "$repo_root/skills/$skill/SKILL.md"
done

grep -Fq 'superpowers:test-driven-development' "$repo_root/README.md"
grep -Fq 'smolpowers:smol-execute' "$repo_root/README.md"

if [[ ! -x "$upstream_root/skills/subagent-driven-development/scripts/task-brief" ]]; then
  printf 'SKIP: set SUPERPOWERS_ROOT to an upstream Superpowers checkout\n'
  exit 0
fi

for skill in brainstorming writing-plans subagent-driven-development; do
  skill_file="$upstream_root/skills/$skill/SKILL.md"
  test -f "$skill_file"
  grep -q "workflow_owner" "$skill_file"
  grep -q "return_to_caller" "$skill_file"
done

grep -q "output_path" "$upstream_root/skills/brainstorming/SKILL.md"
grep -q "output_path" "$upstream_root/skills/writing-plans/SKILL.md"
grep -q "tracked_artifact" "$upstream_root/skills/brainstorming/SKILL.md"
grep -q "tracked_artifact" "$upstream_root/skills/writing-plans/SKILL.md"

test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT
plan="$test_root/plan.md"
brief="$test_root/task-1.md"
sed 's/Task N/Task 1/' \
  "$repo_root/skills/smol-plan/references/plan-template.md" >"$plan"
"$upstream_root/skills/subagent-driven-development/scripts/task-brief" \
  "$plan" 1 "$brief" >/dev/null
grep -q '^### Task 1:' "$brief"
grep -q '^\*\*Files:\*\*' "$brief"
grep -q '^\*\*Outcome:\*\*' "$brief"

printf 'Actual upstream substitution tests passed\n'
