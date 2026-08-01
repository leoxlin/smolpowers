---
name: smol-activate
description: Start or continue Smolpowers for important software changes. Route work through the first incomplete Design → Plan → Execute → Finish phase.
---

<IMPORTANT>
- Ignore this skill as a subagent with a specific task.
- Use `design` → `plan` → `execute` → `finish` in sequence.
- Write artifacts in ASD-STE100.
</IMPORTANT>

## Load Configuration

- Run [load-config.py](scripts/load-config.py) from this skill root with Python 3.10 or later. Use `python3`, `python`, or `py -3`. Pass the repository root or require Git.
- Save the JSON as `SMOL_CONFIG`. Use `specDir` for artifacts and `stateDir` for information only.

Read `SMOL_CONFIG.activation` before phase selection:

- `manual`: Use for an explicit Smolpowers request.
- `default`: Use for an important change.
- `always`: Use for every change, except questions or a requested different workflow.

Use the normal process if the request does not match the level.

## Select a Phase

1. Use the user-specified artifact or slug. Otherwise, match the request to an artifact pair.
2. Examine these files:
   - Design Spec: `<specDir>/specs/YYYY-MM-DD-<slug>-design.md`
   - Implementation Plan: `<specDir>/plans/YYYY-MM-DD-<slug>.md`
   - Plan status: `**Status:** Active` or `**Status:** Complete`

Select the first match:

1. `design` if the Design Spec is absent, incomplete, incorrect, or stale.
2. `plan` if the Implementation Plan is absent, incomplete, incorrect, or stale.
3. `execute` if an Implementation Plan task is incomplete or its verification fails.
4. `finish` if all Implementation Plan tasks pass verification and its status is `Active`.

Stop for `Complete` status. Read [lifecycle.md](references/lifecycle.md) if selection is unclear.

## Start a Phase

1. Select the requested phase skill or `SMOL_CONFIG.phases.<phase>.owner`.
2. Use `smol-<phase>` if the owner is invalid, unavailable, or cannot load.
3. Activate relevant `SMOL_CONFIG.phases.<phase>.companions`.
4. Activate the selected owner.

## Continue Automatically

- Return to an earlier phase for a stale artifact. Do not omit a phase.
- A change request approves all phases.
- Pause for important ambiguity, larger scope, destructive action, or external effect.
- After each phase, select again. Stop early only for a Design-only or Plan-only request.
