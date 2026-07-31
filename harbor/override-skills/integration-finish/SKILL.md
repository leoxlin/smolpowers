---
name: integration-finish
description: Test-only Finish owner for the configuration override integration fixture.
---

# Integration Finish Owner

Own only the Finish phase of the integration fixture.

1. Locate and run the Harbor-injected `smol-activate` configuration loader beneath the agent's installed skill directories. Do not assume the skill is inside the project. Parse its JSON without `eval`, and require the exact spec and plan passed by Execute beneath `specDir`.
2. Append `finish|<specDir>|<stateDir>` to `<stateDir>/phase-calls.log`, using the absolute loader values.
3. Verify the spec and plan exist, the plan has no `- [ ]` task, and `python -m unittest discover -s tests` passes.
4. Verify the phase names in `<stateDir>/phase-calls.log` are exactly `design`, `plan`, `execute`, and `finish` in that order.
5. Verify `app.py` differs from `HEAD`, while `.gitignore`, `.smolpowers.json`, `requirements.txt`, and `tests/test_api.py` do not.
6. Verify neither repository-root `docs/superpowers` nor `.superpowers` exists.
7. Report the verified lifecycle complete without committing or performing another Git action.
