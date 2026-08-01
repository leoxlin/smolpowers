# Completion Verification

## Evidence matrix

For each requirement, record:

| Requirement | Implementation evidence | Verification command | Result |
|---|---|---|---|
| [Exact Design Spec statement] | [File, behavior, or diff] | `[fresh command]` | [Exit status and count] |

Inspect untracked files as part of the diff. Separate pre-existing user changes from lifecycle work.

## Freshness

Run each unique command after the final code change. Read the complete output and exit status. A focused test does not
prove the build. A linter does not prove runtime behavior. A prior run does not prove current state.

For unavailable integrations, record the executable checked, version if available, command attempted, and exact authentication or availability failure.
