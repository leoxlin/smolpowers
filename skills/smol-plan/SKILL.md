---
name: smol-plan
description: Make a Smolpowers implementation plan from a current specification. Use when the plan is absent, incomplete, or stale.
---

# Smol Plan

Validate the product specification. Write an implementation plan that an agent can do.

Follow [configuration.md](../smol-activate/references/configuration.md) and apply the configured `plan` phase.

A user request for `writing-plans` replaces this phase. Use the [upstream contract](../smol-activate/references/compatibility.md).

Otherwise, start each companion in its configured sequence. If a different skill owns the phase, start it and stop.

## Validate the Prerequisite

Require a current specification at this path:

`<specDir>/specs/YYYY-MM-DD-<slug>-design.md`

Compare the specification with the request and repository facts.

The specification is stale if its goal, constraints, or approach do not describe the requested work.

If the specification is not current, start the configured `design` phase and stop.

## Shape the Implementation

Examine the applicable code paths and tests. Specify this information:

- The smallest implementation that satisfies the specification
- The file responsibilities and public interfaces
- The data flow and lifecycle owner
- The failure behavior and recovery path
- The task limits and observable results
- The test-first steps and exact final checks

Do not require worktrees, future abstractions, or subagents. Keep setup and documents with the task that needs them.

Read [interfaces-and-failures.md](references/interfaces-and-failures.md) if an interface, migration, or cleanup path is complex.

## Write the Implementation Plan

Write this file:

`<specDir>/plans/YYYY-MM-DD-<slug>.md`

Use [plan-template.md](references/plan-template.md). Keep these elements:

- `Goal`, `Architecture`, and `Global Constraints`
- Numbered `### Task N` headings
- `Files`, `Outcome`, and interface details
- Checkbox steps
- Exact verification commands and expected results

Replace each placeholder. Give each task all necessary information. Make sure that all interface definitions agree.

Write the complete artifact in ASD-STE100. Review it for these problems:

- A missing specification requirement
- A placeholder or missing failure case
- An inconsistent name or interface
- A command that cannot prove its result
- An unapproved word, long sentence, contraction, passive sentence, or semicolon

Correct each problem before you report the phase result.

## Transition

If the user requested implementation, start the configured `execute` phase. Give it the exact artifact paths.

If the user requested only a plan, report the artifact path and stop.
