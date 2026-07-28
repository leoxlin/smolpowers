---
name: integration-finish
description: Test-only Finish owner for the configuration override integration fixture.
---

# Integration Finish Owner

Own only the Finish phase of the integration fixture.

1. Run the configuration loader, parse its JSON without `eval`, and require the exact spec and plan passed by Execute beneath `docsRoot`.
2. Append `finish|<docsRoot>|<stateRoot>` to `<stateRoot>/phase-calls.log`, using the absolute loader values.
3. Verify the spec and plan exist, the plan has no `- [ ]` task, and `result.txt` contains exactly `override lifecycle passed` plus a newline.
4. Verify the phase names in `<stateRoot>/phase-calls.log` are exactly `design`, `plan`, `execute`, and `finish` in that order.
5. Verify neither repository-root `docs/superpowers` nor `.superpowers` exists.
6. Report the verified lifecycle complete without committing or performing another Git action.
