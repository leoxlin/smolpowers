---
name: smol-plan
description: Establish the goal, success criteria, scope, and chosen product approach, then write the Smolpowers design spec. Use for new work, behavior changes, bugs without a current spec, or whenever the Plan phase is the earliest incomplete lifecycle phase.
---

# Smol Plan

Inspect context, decide what to build, and produce the product design artifact.

## Plan the Product

Inspect the repository, current documentation, recent relevant changes, and the user's request before proposing an approach.

For a bug, reproduce the reported behavior or record the exact environmental blocker before choosing a fix. Read [debugging-and-testing.md](references/debugging-and-testing.md) when reproduction, root-cause tracing, or test strategy needs more detail.

Establish:

- the concrete goal and observable success criteria;
- in-scope and out-of-scope behavior;
- constraints and compatibility requirements;
- the current behavior or root cause for bugs;
- viable approaches and their material tradeoffs;
- one chosen product approach.

Use reasonable defaults for minor details. Pause only when different answers would materially change scope, behavior, destructive impact, or external effects.

## Write the Spec

Load configuration through the `smol-activate` loader. Write:

`<docsRoot>/specs/YYYY-MM-DD-<slug>-design.md`

Use [spec-template.md](references/spec-template.md). Replace every placeholder with concrete content and preserve its core headings. Create parent directories only when they are inside an authorized writable location.

Review the written spec for:

- missing requirements or success criteria;
- placeholders and vague language;
- contradictions between scope and approach;
- assumptions that repository evidence disproves;
- work unrelated to the request.

Fix those issues in the artifact before reporting the phase outcome.

## Transition

If implementation was requested, invoke `smol-design` with the exact spec path and configured `docsRoot`.

If only a product plan or specification was requested, report the artifact path and stop.

If the user explicitly requested an upstream product-design skill, let it own this phase and pass the exact custom spec path. Do not create a duplicate Smolpowers spec.
