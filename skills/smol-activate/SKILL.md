---
name: smol-activate
description: Route applicable work through the first incomplete Design → Plan → Execute → Finish phase. Use when the user requests Smolpowers or a large change.
---

# Smol Activate

Load the configuration. Apply the activation level. Examine the artifacts. Start one phase when the request is applicable.

Write all Smolpowers text in ASD-STE100 Simplified Technical English.

## Bootstrap

Follow [configuration.md](references/configuration.md). Load the repository root, configured roots, activation level, and phase objects.

## Activation

Use the configured activation level:

| Level | Activate Smolpowers for |
|---|---|
| `lite` | A request to use or continue Smolpowers. |
| `full` | `lite` work, new features, large refactors, and other important changes. |
| `ultra` | `full` work and each requested code change. |

If the request is not applicable, use the normal agent process.

Read [lifecycle.md](references/lifecycle.md) if the correct phase is not clear.

Read [compatibility.md](references/compatibility.md) if an upstream Superpowers skill owns the phase.

## Select One Phase

Examine the request, the repository, and these artifacts:

- `<specDir>/specs/YYYY-MM-DD-<slug>-design.md`
- `<specDir>/plans/YYYY-MM-DD-<slug>.md`

Use an artifact or slug that the user gives. Otherwise, use the artifact pair that agrees with the request.

Start only one configured phase:

1. Start `design` if the product specification is absent, incomplete, incorrect, or stale.
2. Start `plan` if the specification is current and the implementation plan is not current.
3. Start `execute` if a plan task or its verification is not complete.
4. Start `finish` if all plan tasks are complete and the change needs final verification.

If task tracking is available, make one task record for each unchecked plan task.

Return to a prerequisite phase if its artifact is stale. Do not omit a missing phase.

An upstream skill that the user requests replaces the configured phase.

Follow the contract in [compatibility.md](references/compatibility.md). Continue with the next incomplete phase when the upstream skill returns.

## Continue Automatically

Treat a request to build, change, or correct as approval to continue through the lifecycle.

Pause for an important ambiguity, larger scope, destructive action, or external effect.

Stop after the requested artifact if the user requests only a design or a plan.

Do not create worktrees, use subagents, push, publish, or write external files without approval.
