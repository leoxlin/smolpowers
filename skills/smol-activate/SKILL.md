---
name: smol-activate
description: Start or continue Smolpowers for explicit requests, new features, large refactors, and important changes. Route work through the first incomplete Design → Plan → Execute → Finish phase.
---

Smolpowers is now active 🐹

<IMPORTANT>
- Ignore this skill if you are a subagent with a specific task.
- Activate the applicable Smolpowers skills.
- Write Smolpowers text in ASD-STE100.
- Use this order: `design` → `plan` → `execute` → `finish`.
- Do not skip, reorder, or run phases in parallel.
</IMPORTANT>

## Configuration

- Run `python3 <smol-activate>/scripts/load-config.py`. 
- Save its output as `SMOL_CONFIG`. 
- Use `specDir` for artifacts and `stateDir` for information only.

Read `SMOL_CONFIG.activation` before phase selection:

- `manual`: Activate for explicit smolpowers requests.
- `default`: Activate for new features, large refactors, and important changes.
- `always`: Activate for every change. Do not activate for questions or a requested different workflow. 

Use the normal process if the request does not match the level.

## Phase

1. Use an artifact or slug that the user gives. Otherwise, use the artifact pair that agrees with the request.
2. Examine the request, repository, and artifacts:
   - Design Spec: `<specDir>/specs/YYYY-MM-DD-<slug>-design.md`
   - Implementation Plan: `<specDir>/plans/YYYY-MM-DD-<slug>.md`

Select only the FIRST matching phase:

1. `design` if the Design Spec is absent, incomplete, incorrect, or stale.
2. `plan` if the Implementation Plan is absent, incomplete, incorrect, or stale.
3. `execute` if an Implementation Plan task is incomplete or its verification fails.
4. `finish` if all Implementation Plan tasks pass verification and Finish is incomplete.

Stop if Finish is complete. Read [lifecycle.md](references/lifecycle.md) if selection is unclear.

## Start a Phase

1. Select the requested phase skill, or `SMOL_CONFIG.phases.<phase>.owner`.
2. Use `smol-<phase>` if the owner is invalid.
3. Activate relevant `SMOL_CONFIG.phases.<phase>.companions`.
4. Activate the selected owner.

## Continue Automatically

- Return to previous phase for a stale artifact. Do not omit a missing phase.
- A build, change, or correction request approves all phases.
- Pause for important ambiguity, larger scope, destructive action, or external effect.
- After a phase owner completes, select the first matching phase again.
- Stop after Design only if the user requested only a Design Spec.
- Stop after Plan only if the user requested only an Implementation Plan.
- Stop when Finish completes.
