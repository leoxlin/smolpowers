---
name: smol-plan
description: Make a Smolpowers Implementation Plan from a current Design Spec. Use when the Implementation Plan is absent, incomplete, or stale.
---

Validate the Design Spec. Write an Implementation Plan that an agent can do.
Require `SMOL_CONFIG` and a selected slug from `smol-activate`. If either value is absent, activate `smol-activate` and stop.
Require a current Design Spec at this path:

`<specDir>/specs/YYYY-MM-DD-<slug>-design.md`

Compare the Design Spec with the request and repository facts. The Design Spec is stale if its goal, constraints, or
approach do not describe the requested work. If the Design Spec is not current, return to the phase routing in
`smol-activate`.

## Keep the Plan Small

Plan the smallest solution that satisfies all requirements.
- Omit work that does not need to exist.
- Reuse current patterns.
- Prefer the standard library, native platform, and installed dependencies.
- Do not add unrequested abstractions or future scaffolding.
- Make the shortest change at the root cause.

## Shape the Implementation

Examine the applicable code paths and tests. Specify this information:
- The smallest implementation that satisfies the Design Spec
- The file responsibilities and public interfaces
- The data flow and lifecycle owner
- The failure behavior and recovery path
- The task limits and observable results
- The test-first steps and exact final checks

Read [interfaces-and-failures.md](references/interfaces-and-failures.md) if an interface, migration, or cleanup path is
complex.

## Write the Implementation Plan

Write this file:

`<specDir>/plans/YYYY-MM-DD-<slug>.md`

Use [plan-template.md](references/plan-template.md). Keep these elements:

- `Status`, `Goal`, `Architecture`, and `Global Constraints`
- Numbered `### Task N` headings
- `Files`, `Outcome`, and interface details
- Checkbox steps
- Exact verification commands and expected results

Replace each placeholder, give each task all necessary information. Make sure that all interface definitions agree.

Review it for these problems:
- A missing Design Spec requirement
- A placeholder or missing failure case
- An inconsistent name or interface
- A missing or invalid `Status` value
- A command that cannot prove its result
- An unapproved word, long sentence, contraction, passive sentence, or semicolon

Correct each problem before you report the phase result.

## Transition

Report the exact Implementation Plan path and the configured roots. Follow `smol-activate` for phase routing.
