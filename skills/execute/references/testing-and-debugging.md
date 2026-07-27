# Proportional Test-First Execution

## Behavior changes

Use red → green:

1. Add one check for the next behavior.
2. Run it and confirm the expected behavioral failure.
3. Make the minimum production change.
4. Run the focused and neighboring checks.

Do not weaken a correct test to make code pass.

## Direct validation

Use direct validation for static manifests, generated files, docs, shell syntax, and configuration-only changes when a unit test would merely restate the file. Prefer an existing schema validator, parser, linter, or executable smoke command.

## Unexpected failures

Read the complete error. Reproduce it. Inspect recent relevant changes and every caller of the failing shared path. Form one root-cause hypothesis and test it with the smallest diagnostic. After three failed fixes, stop and question the implementation shape before trying another.
