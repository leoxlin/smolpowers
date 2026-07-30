---
name: smol-execute
description: Do a current Smolpowers plan with configured test-first checks. Use when a plan task or its verification is incomplete.
---

# Smol Execute

Review the plan. Do each remaining task. Keep each checkbox correct.

Follow [configuration.md](../smol-activate/references/configuration.md) and apply the configured `execute` phase.

A requested upstream Execute skill replaces this phase. Use the [upstream contract](../smol-activate/references/compatibility.md).

Otherwise, start each companion in its configured sequence. If a different skill owns the phase, start it and stop.

## Validate and Review

Require the specification and plan for the same slug. Both artifacts must use ASD-STE100.

Start `design` if the specification is absent or stale.

Start `plan` if the plan is absent, stale, inconsistent, or not verifiable. Start only the prerequisite phase and stop.

Read the complete plan before you edit files. Resolve only a conflict that blocks the work.

Examine the worktree before you change it. Keep unrelated user changes.

## Implement Tasks

Do unchecked tasks in sequence unless the plan identifies independent tasks.

If task tracking is available, make one task record for each unchecked task.

Set a task to `in_progress` before the change. Set it to `completed` only after its checks pass.

Read [test-driven-development.md](references/test-driven-development.md). Use the mode in `phases.execute.tdd` for each production behavior change.

Use the smallest direct check for configuration, documents, generated files, or harness metadata. Record the reason in the task result.

If a check has an unexpected failure, find the cause before you edit. Read [debugging.md](references/debugging.md).

## Use Subagents

Do the work directly by default. Read [delegation.md](references/delegation.md) only if subagents are available and useful.

Use subagents only for independent tasks, separate research, or an important review.

The primary agent must examine each result and run the complete verification. Do not require subagents.

## Transition

After each plan task has a verified result, start the configured `finish` phase. Give it the exact artifact paths.

Do not push, publish, or cause another external effect without user approval.
