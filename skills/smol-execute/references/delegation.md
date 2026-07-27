# Optional Delegation

Delegate only when the harness supports it and one of these conditions holds:

- at least two tasks edit non-overlapping files and have no dependency;
- bounded exploration would otherwise require several unrelated searches;
- a security, migration, or compatibility risk justifies an independent review.

Give each worker one bounded outcome, exact allowed paths, relevant artifact paths, and exact verification. Do not assign the same file to concurrent workers.

The primary agent must:

1. inspect every returned change;
2. resolve integration conflicts;
3. run the focused checks;
4. run the complete verification;
5. keep plan checkboxes and evidence truthful.

If these conditions do not hold, execute directly.
