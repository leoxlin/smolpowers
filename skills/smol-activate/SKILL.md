---
name: smol-activate
description: Bootstrap the lightweight Plan → Design → Execute → Finish lifecycle, load repository Smolpowers configuration, and route to the earliest incomplete phase. Use at session start, after compaction, when resuming work, or when a coding request has not already selected a phase skill.
---

# Smol Activate

Load configuration, inspect the artifact pair, and invoke exactly one phase owner.

## Bootstrap

Load the repository root with `git rev-parse --show-toplevel`.

Locate `scripts/load-config.sh` in this skill directory and run:

```bash
bash /absolute/path/to/smol-activate/scripts/load-config.sh /absolute/repo/root
```

Parse its JSON output directly. Never use `eval`. Treat `docsRoot` as the artifact root and `stateRoot` as information only. Core Smolpowers never writes `stateRoot`.

Read [lifecycle.md](references/lifecycle.md) when choosing a phase is not obvious. Read [compatibility.md](references/compatibility.md) when the user explicitly requests an upstream Superpowers skill or the active harness needs a tool mapping.

## Select One Phase

Inspect the user's request, relevant repository state, and artifacts under:

- `<docsRoot>/specs/YYYY-MM-DD-<slug>-design.md`
- `<docsRoot>/plans/YYYY-MM-DD-<slug>.md`

Prefer an explicitly named artifact or slug. Otherwise choose the artifact pair most clearly associated with the request; do not select an unrelated file merely because it is newest.

Invoke exactly one owner:

1. Invoke `smol-plan` when the product spec is missing, incomplete, contradicted by the current request, or based on repository facts that materially changed.
2. Invoke `smol-design` when the spec is current but its implementation plan is missing, incomplete, or no longer implements the spec.
3. Invoke `smol-execute` when the plan is current and any task remains unchecked, or when implementation exists but the plan and checks have not been reconciled.
4. Invoke `smol-finish` when all plan tasks are complete and the implementation needs final requirements, diff, verification, or Git handling.

Route backward on stale prerequisites. Do not skip a missing phase.

If the user explicitly requests a corresponding upstream skill, invoke that skill as the phase owner instead of its Smolpowers counterpart. Pass the configured artifact path in the invocation. Do not wrap it, duplicate its work, or invoke a second phase.

## Continue Automatically

Treat requests to build, implement, change, or fix as authorization to advance through the lifecycle. Each phase owns its own transition to the next phase.

Pause only for material ambiguity, scope expansion, destructive operations, or external side effects. Stop after the requested artifact when the user asked only for planning or design.

Do not create worktrees, dispatch subagents, push, open pull requests, publish, or write external paths unless the request and normal approval rules authorize them.
