---
name: smol-design
description: Make a Smolpowers Design Spec. Use when the Design Spec is absent, incomplete, or stale.
---

Examine the context. Select the product change. Write the Design Spec.

## Design the Product

Examine the repository, current documents, applicable changes, and the user request before you select an approach. For a
defect, reproduce the reported behavior. If this is not possible, record the exact environment problem.

Read [debugging-and-testing.md](references/debugging-and-testing.md) if you need more test or cause information.

Specify this information:
- The goal and observable success criteria
- The included and excluded behavior
- The constraints and compatibility requirements
- The current behavior or defect cause
- The possible approaches and important differences
- The selected product approach

Use reasonable values for small details. Pause only if an answer can change scope, behavior, damage risk, or external
effects.

## Write the Design Spec

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

Report the exact Design Spec path and the configured roots. Do not start another skill or phase. `smol-activate` owns
all phase routing.
