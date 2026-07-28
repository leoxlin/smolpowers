---
name: integration-plan
description: Test-only Plan owner for the configuration override integration fixture.
---

# Integration Plan Owner

Own only the Plan phase of the integration fixture.

1. Run the configuration loader, parse its JSON without `eval`, and require the exact current spec passed by Design beneath `docsRoot`.
2. Append `plan|<docsRoot>|<stateRoot>` to `<stateRoot>/phase-calls.log`, using the absolute loader values.
3. Write the matching `<docsRoot>/plans/<date>-override-lifecycle.md`. Include one unchecked task to create repository-root `result.txt` with exactly `override lifecycle passed` plus a newline, verify it with `test "$(cat result.txt)" = "override lifecycle passed"`, then check the task.
4. Invoke the configured Execute owner, `integration-execute`, with the repository root, configured roots, active request, exact spec path, and exact plan path.

Do not perform Execute, Finish, or Git work yourself.
