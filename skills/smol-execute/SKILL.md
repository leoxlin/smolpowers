---
name: smol-execute
description: Do a current Smolpowers Implementation Plan with configured test-first checks. Use when an Implementation Plan task or its verification is incomplete.
---

Review the Implementation Plan. Do each remaining task. Keep each checkbox correct. Require the Design Spec and
Implementation Plan for the same slug. If the Design Spec or Implementation Plan is absent, stale, inconsistent, or not
verifiable, return to the phase routing in `smol-activate`.

Read the complete Implementation Plan before you edit files. Resolve only a conflict that blocks the work. Examine the
worktree before you change it. Keep unrelated user changes.

## Implement Tasks

- Do unchecked tasks in sequence unless the Implementation Plan identifies independent tasks.
- If task tracking is available, make one task record for each unchecked task.
- Set a task to `in_progress` before the change. Set it to `completed` only after its checks pass.
- Read [test-driven-development.md](references/test-driven-development.md). Use the mode in `phases.execute.tdd` for
  each production behavior change.

Use the smallest direct check for configuration, documents, generated files, or harness metadata. Record the reason in
the task result.

If a check has an unexpected failure, find the cause before you edit. Read [debugging.md](references/debugging.md).

## Use Subagents

- Do the work directly by default. Do not require subagents.
- The primary agent must examine each result and run the complete verification. 
- Use subagents only for independent tasks, separate research, or an important review.
- Ensure the subagent receive all required context to work effectively
- Read [delegation.md](references/delegation.md) only if subagents are available and useful.

## Transition

Report the exact Implementation Plan path and the task results. Follow `smol-activate` for phase routing. Do not push,
publish, or cause another external effect without user approval.
