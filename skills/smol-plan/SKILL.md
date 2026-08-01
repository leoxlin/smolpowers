---
name: smol-plan
description: Make a Smolpowers Implementation Plan from a current Design Spec. Use when the Implementation Plan is absent, incomplete, or stale.
---

Validate the Design Spec. Write an Implementation Plan that an agent can do.
Require a current Design Spec at this path:

`<specDir>/specs/YYYY-MM-DD-<slug>-design.md`

Compare the Design Spec with the request and repository facts. The Design Spec is stale if its goal, constraints, or
approach do not describe the requested work. If the Design Spec is not current, return to the phase routing in
`smol-activate`.

## Keep it SIMPLE Stupid

Plan the SMALLEST solution that works, and satisfies all requirements. Keep simplicity in mind.
- Does it need to exist? (YAGNI)
- Reuse Exiting Patterns?
- Use STDLIB?
- Use Native Platform?
- Use Existing Dependency?
- No unrequested abstractions or "for later" scaffolding
- Shortest diff at the root cause

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

- `Goal`, `Architecture`, and `Global Constraints`
- Numbered `### Task N` headings
- `Files`, `Outcome`, and interface details
- Checkbox steps
- Exact verification commands and expected results

Replace each placeholder, give each task all necessary information. Make sure that all interface definitions agree.

Review it for these problems:
- A missing Design Spec requirement
- A placeholder or missing failure case
- An inconsistent name or interface
- A command that cannot prove its result
- An unapproved word, long sentence, contraction, passive sentence, or semicolon

Correct each problem before you report the phase result.

## Transition

Report the exact Implementation Plan path and the configured roots. Follow `smol-activate` for phase routing.
