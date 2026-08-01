# Optional Delegation

Delegate only when the harness supports it and one of these conditions holds:

- At least two tasks edit non-overlapping files and have no dependency.
- Bounded exploration would otherwise require several unrelated searches.
- A security, migration, or compatibility risk justifies an independent review.

Give each worker one bounded outcome, exact allowed paths, relevant artifact paths, and exact verification. Do not assign the same file to concurrent workers.

The primary agent must:

1. Inspect every returned change.
2. Resolve integration conflicts.
3. Run the focused checks.
4. Run the complete verification.
5. Keep Implementation Plan checkboxes and evidence truthful.

If these conditions do not hold, execute directly.
