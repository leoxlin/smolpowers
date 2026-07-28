---
name: smol-execute
description: Execute a current Smolpowers plan with configurable test-driven checks. Use when plan tasks or their verification remain incomplete.
---

# Smol Execute

Review the plan, implement every remaining task, and keep its checkboxes truthful.

Resolve and apply the configured `execute` phase chain by following [configuration.md](../smol-activate/references/configuration.md). An explicitly requested `superpowers:subagent-driven-development` or `superpowers:executing-plans` overrides the entire chain; use the [upstream contract](../smol-activate/references/compatibility.md). Otherwise, if the chain's owner is another skill, invoke that chain and stop this phase.

## Validate and Review

Require both the spec and plan artifact for the same slug.

Route to the configured `design` phase chain when the spec is missing or stale. Route to the configured `plan` phase chain when the plan is missing, contradicts the spec, relies on materially changed repository facts, or lacks executable verification. Invoke only the prerequisite phase and stop.

Read the complete plan before editing. Resolve only blocking contradictions; do not reopen settled product choices because another approach is merely possible.

Inspect the worktree before changing it. Preserve unrelated user changes and never treat a dirty tree as permission to discard them.

## Implement Tasks

Execute unchecked tasks in order unless the plan explicitly marks them independent.

Read [test-driven-development.md](references/test-driven-development.md) and follow the mode matching the loaded `tdd` value for every new feature, bug fix, refactor, or production behavior change.

Configuration-only, documentation-only, generated, or harness-metadata changes that do not alter production behavior may use the narrowest direct validation. Record why in the task outcome.

When a check fails unexpectedly, investigate the root cause before editing. Read [debugging.md](references/debugging.md) for the bounded workflow.

## Delegate Sparingly

Execute directly by default. Read [delegation.md](references/delegation.md) only when delegation is available and potentially useful.

Delegate only for at least two independent, non-overlapping tasks, bounded exploration, or risk-justified review. Keep dependent edits sequential. The primary agent integrates every result, inspects the diff, and runs the complete verification.

Do not require subagents. Continue directly when the harness lacks them.

## Transition

After every plan task has a verified outcome, invoke the configured `finish` phase chain with the exact spec and plan paths.

Do not push, open a pull request, publish, or perform another external side effect unless the user explicitly authorized it.
