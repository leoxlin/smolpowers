---
name: integration-execute
description: Test-only Execute owner for the configuration override integration fixture.
---

# Integration Execute Owner

Own only the Execute phase of the integration fixture.

1. Run the configuration loader, parse its JSON without `eval`, and require the exact spec and plan passed by Plan beneath `docsRoot`.
2. Append `execute|<docsRoot>|<stateRoot>` to `<stateRoot>/phase-calls.log`, using the absolute loader values.
3. Create repository-root `result.txt` with exactly `override lifecycle passed` plus a newline.
4. Run `test "$(cat result.txt)" = "override lifecycle passed"`. Only after it passes, mark the plan's single task checked.
5. Invoke the configured Finish owner, `integration-finish`, with the repository root, configured roots, active request, exact spec path, and exact plan path.

Do not perform Finish or Git work yourself.
