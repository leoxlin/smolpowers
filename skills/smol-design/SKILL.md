---
name: smol-design
description: Convert a current Smolpowers product spec into an upstream-compatible implementation plan with tasks, interfaces, failure handling, and exact checks. Use after Plan, when a spec exists but its implementation plan is missing or stale, or when explicitly asked for the Design phase.
---

# Smol Design

Validate the product spec and produce an executable implementation plan.

If the user explicitly requested `superpowers:writing-plans`, invoke it before doing Design work using the [upstream contract](../smol-activate/references/compatibility.md), then stop this phase.

## Validate the Prerequisite

Load configuration through `smol-activate`. Require a current spec at:

`<docsRoot>/specs/YYYY-MM-DD-<slug>-design.md`

Compare the spec to the active request and relevant repository facts. Treat it as stale when its goal, constraints, or chosen approach no longer describe the requested work. If it is missing, incomplete, or stale, invoke `smol-plan` with the configured spec path and stop this phase.

## Shape the Implementation

Inspect the code paths and tests the spec affects. Define:

- the smallest implementation shape that satisfies the spec;
- file responsibilities and public interfaces;
- data flow and lifecycle ownership;
- failure behavior and recovery paths;
- task boundaries that yield independently verifiable outcomes;
- proportional test-first steps and exact final checks.

Avoid mandatory worktrees, speculative abstractions, and unconditional delegation. Keep setup and documentation with the task whose outcome needs them.

Read [interfaces-and-failures.md](references/interfaces-and-failures.md) when a boundary, error contract, migration, or cleanup path is non-trivial.

## Write the Implementation Plan

Write:

`<docsRoot>/plans/YYYY-MM-DD-<slug>.md`

Use [plan-template.md](references/plan-template.md). Preserve these upstream-consumable elements:

- `Goal`, `Architecture`, and `Global Constraints`;
- numbered `### Task N` headings;
- `Files`, `Outcome`, and interface details;
- checkbox steps;
- exact verification commands and expected results.

Replace every placeholder. Make each task understandable without relying on “similar to Task N” or unstated context. Ensure later task interfaces match earlier definitions.

Review the final plan against every spec requirement, then scan for placeholders, missing failure cases, inconsistent names, and commands that cannot prove their stated outcome.

## Transition

If implementation was requested, invoke `smol-execute` with the exact spec and plan paths.

If only an implementation plan was requested, report the artifact path and stop.
