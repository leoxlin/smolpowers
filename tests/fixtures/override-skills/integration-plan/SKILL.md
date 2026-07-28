---
name: integration-plan
description: Test-only Plan owner for the configuration override integration fixture.
---

# Integration Plan Owner

Own only the Plan phase of the integration fixture.

1. Locate and run the Harbor-injected `smol-activate` configuration loader beneath the agent's installed skill directories. Do not assume the skill is inside the project. Parse its JSON without `eval`, and require the exact current spec passed by Design beneath `specDir`.
2. Append `plan|<specDir>|<stateDir>` to `<stateDir>/phase-calls.log`, using the absolute loader values.
3. Write the matching `<specDir>/plans/<date>-override-lifecycle.md`. Include one unchecked task to create repository-root `result.txt` with exactly `override lifecycle passed` plus a newline, verify it with `test "$(cat result.txt)" = "override lifecycle passed"`, then check the task.
4. Invoke the configured Execute owner, `integration-execute`, with the repository root, configured roots, active request, exact spec path, and exact plan path.

Do not perform Execute, Finish, or Git work yourself.
