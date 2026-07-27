# Harness and Upstream Compatibility

## Explicit upstream ownership

| Requested upstream skill | Smolpowers phase | Handoff |
|---|---|---|
| `superpowers:brainstorming` | Plan | Pass `<docsRoot>/specs/YYYY-MM-DD-<slug>-design.md` as the required spec path. |
| `superpowers:writing-plans` | Design | Pass the current spec and `<docsRoot>/plans/YYYY-MM-DD-<slug>.md`. |
| `superpowers:executing-plans` or `superpowers:subagent-driven-development` | Execute | Pass the exact plan path. |
| `superpowers:finishing-a-development-branch` | Finish | Pass both artifact paths and the authorized Git disposition. |

Do not invoke the Smolpowers counterpart before or after an explicitly requested upstream owner.

Partial installation of these selected upstream skills is supported. Enabling both complete bootstrap plugins simultaneously is not guaranteed. [PLEASE VERIFY]

## Harness tools

| Action | Claude | Codex | Kimi | Pi |
|---|---|---|---|---|
| Invoke skill | `Skill` | native skill invocation | `Skill` | native skill discovery or `/skill:name` |
| Ask a material question | `AskUserQuestion` when available | request-user-input tool when available | `AskUserQuestion` | ask in the session |
| Track tasks | task list tool when available | plan tool | `TodoList` | optional task tool or plan checkboxes |
| Delegate | `Task` | collaboration agent tools | `Agent` | optional subagent extension |
| Search/read/edit/run | native tools | native tools | `Grep`, `Glob`, `Read`, `Edit`, `Bash` | lowercase native coding tools |

Map capabilities, not literal tool names. If delegation is unavailable, execute directly.
