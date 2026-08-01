---
name: smol-finish
description: Finish a Smolpowers change with complete verification and approved Git actions. Use after all Implementation Plan tasks pass.
---

Verify the requirements and the complete change before you report completion. Require a matching Design Spec and
Implementation Plan. If the Design Spec or Implementation Plan is absent or stale, or if a task or its result is
incomplete, report the problem and return to the phase routing in `smol-activate`.

## Verify the Work

Read [verification.md](references/verification.md). Then, do these steps:

1. Connect each Design Spec requirement to implementation evidence.
2. Connect each task result to the diff and verification result.
3. Examine the complete diff, which includes untracked files.
4. Find unwanted scope, placeholders, secrets, debug output, and unrelated changes.
5. Run each exact Implementation Plan command again.
6. Run all applicable test, lint, type, and build commands.
7. Reproduce the original symptom for a defect correction.
8. Record commands, exit status, counts, and omitted coverage.

Do not use partial output or an old result as evidence. Do not report completion if a required check fails.

If verification fails, report the command and failure. Keep the worktree state. Do not correct the code without user
approval.

## Handle Git

Read [git-disposition.md](references/git-disposition.md). Examine the current branch and remotes. Do only the Git action
that the user approved. A local commit does not give approval to push. An implementation request does not give approval
for other Git actions.
