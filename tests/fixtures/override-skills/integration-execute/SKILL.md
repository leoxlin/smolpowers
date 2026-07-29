---
name: integration-execute
description: Test-only Execute owner for the configuration override integration fixture.
---

# Integration Execute Owner

Own only the Execute phase of the integration fixture.

1. Locate and run the Harbor-injected `smol-activate` configuration loader beneath the agent's installed skill directories. Do not assume the skill is inside the project. Parse its JSON without `eval`, and require the exact spec and plan passed by Plan beneath `specDir`.
2. Append `execute|<specDir>|<stateDir>` to `<stateDir>/phase-calls.log`, using the absolute loader values.
3. Change repository-root `greeting.py` so `greeting.greet()` returns exactly `hello from smolpowers`. Preserve the existing test and configuration.
4. Run `python -m unittest tests/test_greeting.py`. Only after it passes, mark the plan's single task checked.
5. Invoke the configured Finish owner, `integration-finish`, with the repository root, configured roots, active request, exact spec path, and exact plan path.

Do not perform Finish or Git work yourself.
