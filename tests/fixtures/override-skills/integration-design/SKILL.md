---
name: integration-design
description: Test-only Design owner for the configuration override integration fixture.
---

# Integration Design Owner

Own only the Design phase of the integration fixture.

1. Resolve the repository root, locate the Harbor-injected `smol-activate/scripts/load-config.sh` beneath the agent's installed skill directories, and run it against the repository root. Do not assume the skill is inside the project. Parse the JSON without `eval`.
2. Append `design|<docsRoot>|<stateRoot>` to `<stateRoot>/phase-calls.log`, using the absolute values returned by the loader.
3. Write `<docsRoot>/specs/<today>-override-lifecycle-design.md` with `Status: Current`. Its required outcome is a repository-root `result.txt` containing exactly `override lifecycle passed` plus a newline.
4. Invoke the configured Plan owner, `integration-plan`, with the repository root, configured roots, active request, and exact spec path.

Do not perform Plan, Execute, Finish, or Git work yourself.
