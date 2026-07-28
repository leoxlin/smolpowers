---
name: smol-activate
description: Route qualifying work through the earliest incomplete Design → Plan → Execute → Finish phase. Use when the user explicitly invokes Smolpowers or requests a new feature, large refactor, or other non-trivial change.
---

# Smol Activate

Load configuration, apply activation, then inspect the artifact pair and invoke exactly one phase object when the request qualifies.

## Bootstrap

Load the repository root, roots, activation level, and phase objects by following [configuration.md](references/configuration.md).

## Activation

Apply the configured activation level:

| Level | Activate Smolpowers for |
|---|---|
| `lite` | Explicit requests to use or resume Smolpowers. |
| `full` | `lite`, plus new features, large refactors, and other non-trivial changes with material scope, behavior, risk, or cross-cutting impact. |
| `ultra` | `full`, plus every requested code change. |

When the request does not qualify, continue with the normal agent workflow.

Read [lifecycle.md](references/lifecycle.md) when choosing a phase is not obvious. Read [compatibility.md](references/compatibility.md) when a configured or explicitly requested owner is an upstream Superpowers skill, or the active harness needs a tool mapping.

## Select One Phase

Inspect the user's request, relevant repository state, and artifacts under:

- `<specDir>/specs/YYYY-MM-DD-<slug>-design.md`
- `<specDir>/plans/YYYY-MM-DD-<slug>.md`

Prefer an explicitly named artifact or slug. Otherwise choose the artifact pair most clearly associated with the request; do not select an unrelated file merely because it is newest.

Invoke exactly one configured phase object:

1. Invoke the configured `design` phase object when the product spec is missing, incomplete, contradicted by the current request, or based on repository facts that materially changed.
2. Invoke the configured `plan` phase object when the spec is current but its implementation plan is missing, incomplete, or no longer implements the spec.
3. Invoke the configured `execute` phase object when the plan is current and any task remains unchecked, or when implementation exists but the plan and checks have not been reconciled.
4. Invoke the configured `finish` phase object when all plan tasks are complete and the implementation needs final requirements, diff, verification, or Git handling.

When selecting Execute, create todos for every unchecked task when task tracking is available; the Execute owner keeps their statuses synchronized.

Route backward on stale prerequisites. Do not skip a missing phase.

If the user explicitly requests a corresponding upstream skill, it overrides
the entire configured phase object for this run. Follow the handoff contract in
[compatibility.md](references/compatibility.md). When a returning owner
completes, continue at the next incomplete configured phase if the request
authorizes it. Do not wrap or duplicate the selected phase.

## Continue Automatically

Treat requests to build, implement, change, or fix as authorization to advance through the lifecycle. Each phase owns its own transition to the next phase.

Pause only for material ambiguity, scope expansion, destructive operations, or external side effects. Stop after the requested artifact when the user asked only for planning or design.

Do not create worktrees, dispatch subagents, push, open pull requests, publish, or write external paths unless the request and normal approval rules authorize them.
