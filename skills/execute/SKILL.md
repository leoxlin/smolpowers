---
name: execute
description: Review and implement a current Smolpowers implementation plan, applying proportional test-first development and fresh task checks. Use when the spec and plan are current and implementation tasks remain, including resuming a partially completed plan.
---

# Execute

Review the plan, implement every remaining task, and keep its checkboxes truthful.

## Validate and Review

Load configuration through `using-smolpowers`. Require both the spec and plan artifact for the same slug.

Route to `plan` when the spec is missing or stale. Route to `design` when the plan is missing, contradicts the spec, relies on materially changed repository facts, or lacks executable verification. Invoke only the prerequisite phase and stop.

Read the complete plan before editing. Resolve only blocking contradictions; do not reopen settled product choices because another approach is merely possible.

Inspect the worktree before changing it. Preserve unrelated user changes and never treat a dirty tree as permission to discard them.

## Implement Tasks

Execute unchecked tasks in order unless the plan explicitly marks them independent.

For each behavior change:

1. Write or identify the smallest check that would fail without the change.
2. Run it and confirm the failure is caused by the missing behavior, when a new automated test is practical.
3. Implement the minimum production change.
4. Run the task's exact check and relevant neighboring checks.
5. Mark a checkbox complete only after its outcome is present and its check passes.

Use test-first development proportionally. Configuration-only, documentation-only, generated, or untestable harness metadata may use direct validation instead of a contrived unit test. Record why in the task outcome.

When a check fails unexpectedly, investigate the root cause before editing. Read [testing-and-debugging.md](references/testing-and-debugging.md) for the bounded workflow.

## Delegate Sparingly

Execute directly by default. Read [delegation.md](references/delegation.md) only when delegation is available and potentially useful.

Delegate only for at least two independent, non-overlapping tasks, bounded exploration, or risk-justified review. Keep dependent edits sequential. The primary agent integrates every result, inspects the diff, and runs the complete verification.

Do not require subagents. Continue directly when the harness lacks them.

## Transition

After every plan task has a verified outcome, invoke `finish` with the exact spec and plan paths.

Do not push, open a pull request, publish, or perform another external side effect unless the user explicitly authorized it.

If the user explicitly requested an upstream execution skill, let it own this phase and pass the exact plan path. Do not run Smolpowers execution in parallel.
