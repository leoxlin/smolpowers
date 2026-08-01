---
name: smol-finish
description: Finish a Smolpowers change with complete verification and approved Git actions. Use after all Implementation Plan tasks pass.
---

Verify the requirements and the complete change before you report completion. Require a matching Design Spec and
Implementation Plan. If the Design Spec or Implementation Plan is absent or stale, or if a task or its result is
incomplete, report the problem and return to the phase routing in `smol-activate`.

Require `SMOL_CONFIG` and a selected slug from `smol-activate`. If either value is absent, activate `smol-activate` and stop.

## Verify the Work

Read [verification.md](references/verification.md). Then, do these steps:

1. Connect each Design Spec requirement to implementation evidence.
2. Connect each task result to the diff and verification result.
3. Examine the complete diff, which includes untracked files.
4. Find unwanted scope, placeholders, secrets, debug output, and unrelated changes.
5. Make one list of unique final verification, test, lint, type, and build commands. Exclude expected-failure commands.
6. Run each command in the list one time after the final code change.
7. Reproduce the original symptom for a defect correction.
8. Record commands, exit status, counts, and omitted coverage.

Do not use partial output or an old result as evidence. Do not report completion if a required check fails.

If verification fails and the request approves implementation, keep the status `Active` and return to Execute. If the
request approves verification only, report the command and failure, keep the worktree state, and stop.

Set the Implementation Plan status to `Complete` only after all required checks pass. A Git delivery failure does not
invalidate verified implementation evidence.

## Handle Git

Read [git-disposition.md](references/git-disposition.md). Examine the current branch and remotes. Do only the Git action
that the user approved. A local commit does not give approval to push. An implementation request does not give approval
for other Git actions.
