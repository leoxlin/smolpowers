---
name: smol-execute
description: Execute a current Smolpowers plan with configurable test-driven checks. Use when plan tasks or their verification remain incomplete.
---

# Smol Execute

Review the plan, implement every remaining task, and keep its checkboxes truthful.

Resolve and apply the configured `execute` phase object by following [configuration.md](../smol-activate/references/configuration.md). An explicitly requested `superpowers:subagent-driven-development` or `superpowers:executing-plans` overrides the entire phase object; use the [upstream contract](../smol-activate/references/compatibility.md). Otherwise, invoke its companions in order. If its owner is another skill, invoke that owner and stop this phase.

## Validate and Review

Require both the spec and plan artifact for the same slug.

Route to the configured `design` phase object when the spec is missing or stale. Route to the configured `plan` phase object when the plan is missing, contradicts the spec, relies on materially changed repository facts, or lacks executable verification. Invoke only the prerequisite phase and stop.

Read the complete plan before editing. Resolve only blocking contradictions; do not reopen settled product choices because another approach is merely possible.

Inspect the worktree before changing it. Preserve unrelated user changes and never treat a dirty tree as permission to discard them.

## Implement Tasks

Execute unchecked tasks in order unless the plan explicitly marks them independent.

When task tracking is available, create todos for every unchecked task. Mark each `in_progress` before implementation and `completed` only after its outcome and checks pass.

Read [test-driven-development.md](references/test-driven-development.md) and follow the mode matching `phases.execute.tdd` for every new feature, bug fix, refactor, or production behavior change.

Configuration-only, documentation-only, generated, or harness-metadata changes that do not alter production behavior may use the narrowest direct validation. Record why in the task outcome.

When a check fails unexpectedly, investigate the root cause before editing. Read [debugging.md](references/debugging.md) for the bounded workflow.

## Delegate Sparingly

Execute directly by default. Read [delegation.md](references/delegation.md) only when delegation is available and potentially useful.

Delegate only for at least two independent, non-overlapping tasks, bounded exploration, or risk-justified review. Keep dependent edits sequential. The primary agent integrates every result, inspects the diff, and runs the complete verification.

Do not require subagents. Continue directly when the harness lacks them.

## Transition

After every plan task has a verified outcome, invoke the configured `finish` phase object with the exact spec and plan paths.

Do not push, open a pull request, publish, or perform another external side effect unless the user explicitly authorized it.
