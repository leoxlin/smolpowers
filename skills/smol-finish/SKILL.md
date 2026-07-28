---
name: smol-finish
description: Finish a Smolpowers change with full-diff verification and authorized Git handling. Use after all plan tasks pass or before completion and Git handoff.
---

# Smol Finish

Verify requirements and the complete change before making any completion claim.

If the user explicitly requested `superpowers:finishing-a-development-branch`, invoke it before doing Finish work using the [upstream contract](../smol-activate/references/compatibility.md), then stop this phase.

## Validate the Lifecycle

Load the repository root, `docsRoot`, and `stateRoot` by following [configuration.md](../smol-activate/references/configuration.md). Require the matching spec and plan.

Route to `smol-plan` if the spec is missing or stale. Route to `smol-design` if the plan is missing or stale. Route to `smol-execute` if any task remains incomplete or its outcome is absent. Invoke only that phase and stop.

## Verify the Work

Read [verification.md](references/verification.md), then:

1. Map every spec requirement to implemented evidence.
2. Map every task outcome to the diff and its verification result.
3. Inspect the complete diff, including untracked files, for scope drift, placeholders, secrets, debug output, missing failure handling, and unrelated changes.
4. Run every exact plan verification command fresh.
5. Run the repository's complete relevant test, lint, type, and build commands.
6. Reproduce the original symptom for bug fixes.
7. Record commands, exit status, pass/fail counts, and any skipped coverage.

Do not infer that a command passed from partial output or an earlier run. Do not call the work complete when any required check is failing.

If verification fails, report the exact command and failure, preserve the working state, and return to `smol-execute` only when a code change is authorized.

## Handle Git

Read [git-disposition.md](references/git-disposition.md), inspect the current branch and remotes, and perform only the disposition already authorized by the user.

A local commit is not authorization to push. A request to implement is not authorization to open a pull request, merge, publish, discard work, or delete a branch. Use conventional commit messages when committing.

Report:

- the artifact paths;
- the implemented outcome;
- fresh verification evidence;
- the resulting commit or exact working-tree state;
- authentication, availability, or integration gaps without claiming unrun coverage.
