---
name: smol-design
description: Make a Smolpowers product specification. Use when the specification is absent, incomplete, or stale.
---

# Smol Design

Examine the context. Select the product change. Write the product specification.

Follow [configuration.md](../smol-activate/references/configuration.md) and apply the configured `design` phase.

A user request for `brainstorming` replaces this phase. Use the [upstream contract](../smol-activate/references/compatibility.md).

Otherwise, start each companion in its configured sequence. If a different skill owns the phase, start it and stop.

## Design the Product

Examine the repository, current documents, applicable changes, and the user request before you select an approach.

For a defect, reproduce the reported behavior. If this is not possible, record the exact environment problem.

Read [debugging-and-testing.md](references/debugging-and-testing.md) if you need more test or cause information.

Specify this information:

- The goal and observable success criteria
- The included and excluded behavior
- The constraints and compatibility requirements
- The current behavior or defect cause
- The possible approaches and important differences
- The selected product approach

Use reasonable values for small details. Pause only if an answer can change scope, behavior, damage risk, or external effects.

## Write the Spec

Write this file:

`<specDir>/specs/YYYY-MM-DD-<slug>-design.md`

Use [spec-template.md](references/spec-template.md). Replace each placeholder and keep the primary headings.

Write the complete artifact in ASD-STE100. Review it for these problems:

- A missing requirement or success criterion
- A placeholder or unclear statement
- A conflict between the scope and the approach
- An assumption that conflicts with repository evidence
- Work that is not part of the request
- An unapproved word, long sentence, contraction, passive sentence, or semicolon

Correct each problem before you report the phase result.

## Transition

If the user requested implementation, start the configured `plan` phase. Give it the exact specification path and configured roots.

If the user requested only a design, report the artifact path and stop.
