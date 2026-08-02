---
name: smol-activate
description: Start or resume Smolpowers for explicit requests and configured design-bearing changes. Exclude read-only and routine work.
---

<IMPORTANT>
- Ignore this skill as a subagent with a specific task.
- Use `design` → `plan` → `execute` → `finish` in sequence.
- Write artifacts in ASD-STE100.
</IMPORTANT>

## Decide Activation

Apply the first matching rule:

1. Use the normal process for an opt-out or another workflow.
2. Activate for an explicit request to start or resume Smolpowers.
3. Use the normal process for a read-only request.
4. Run [load-config.py](scripts/load-config.py) with Python 3.10 or later. Pass the repository root or require Git. Save the JSON as `SMOL_CONFIG`.
5. Use the normal process for `manual`. Activate each remaining repository change for `always`.
6. For `default`, use the normal process for documentation-only, test-only, formatting-only, lint-only, Git-only,
   mechanical, or small known corrections.
7. For `default`, activate for a matching active change, an interface decision, a coordinated refactor across modules,
   or a change to a published interface, persisted data, configuration schema, security, concurrency, resource
   lifecycle, destructive behavior, or external effect.
8. Otherwise, use the normal process. Use it if uncertain.

## Select a Phase

Use the user-specified artifact or slug. Otherwise, match only the accepted change. Examine:

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

Use a requested ordered skill list or `SMOL_CONFIG.phases.<phase>.skills`. Activate it in order. Stop for an invalid or
unavailable skill. The final skill runs the phase.

## Continue Automatically

- Return to an earlier phase for a stale artifact. Do not omit a phase.
- An accepted implementation request approves all phases for its matching change only.
- Pause for important ambiguity, larger scope, destructive action, or external effect.
- After each phase, select again. Stop early only for a Design-only or Plan-only request.
