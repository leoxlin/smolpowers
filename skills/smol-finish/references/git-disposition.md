# Git Disposition

Apply only an already authorized action:

- leave verified changes uncommitted;
- create a local conventional commit;
- push an existing branch;
- open a pull request;
- merge through the repository's normal process.

Before committing, review `git status`, staged diff, and commit message. Never include unrelated user changes. Use
existing conventions for commit message, if there isn't one, use conventional commit message.

## Conventional Commit Message

Use a conventional commit message. Report this information:

- The artifact paths
- The implementation result
- Current verification evidence
- The commit or exact worktree state
- Each authentication, availability, or integration problem
