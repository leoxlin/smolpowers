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
- Save the JSON as `SMOL_CONFIG`. Use `designDir` and `planDir` for artifact locations.

Read `SMOL_CONFIG.activation` before phase selection:

- `manual`: Use for an explicit Smolpowers request.
- `default`: Use for an important change.
- `always`: Use for every change, except questions or a requested different workflow.

Use the normal process if the request does not match the level.

## Select a Phase

1. Use the user-specified artifact or slug. Otherwise, match the request to an artifact pair.
2. Examine these files:
   - Design Spec: `<designDir>/YYYY-MM-DD-<slug>-design.md`
   - Implementation Plan: `<planDir>/YYYY-MM-DD-<slug>.md`
   - Plan status: `**Status:** Active` or `**Status:** Complete`

Select the first match:

1. `design` if the Design Spec is absent, incomplete, incorrect, or stale.
2. `plan` if the Implementation Plan is absent, incomplete, incorrect, or stale.
3. `execute` if an Implementation Plan task is incomplete or its verification fails.
4. `finish` if all Implementation Plan tasks pass verification and its status is `Active`.

Stop for `Complete` status. Read [lifecycle.md](references/lifecycle.md) if selection is unclear.

## Start a Phase

1. Use the requested ordered phase skill list when the user gives one. Otherwise, use
   `SMOL_CONFIG.phases.<phase>.skills`.
2. Activate each skill from first to last.
3. Stop and identify an invalid or unavailable skill.
4. Let the final skill run the phase.

## Continue Automatically

- Return to an earlier phase for a stale artifact. Do not omit a phase.
- A change request approves all phases.
- Pause for important ambiguity, larger scope, destructive action, or external effect.
- After each phase, select again. Stop early only for a Design-only or Plan-only request.
