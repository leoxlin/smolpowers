# Harness and Upstream Compatibility

## Configured or explicit upstream ownership

| Upstream skill | Replaced phase | Handoff |
|---|---|---|
| `superpowers:brainstorming` | Design | Pass `workflow_owner: smolpowers:smol-activate`, the spec path as `output_path`, `tracked_artifact: true`, and `return_to_caller: true`. |
| `superpowers:writing-plans` | Plan | Pass `workflow_owner: smolpowers:smol-activate`, the current spec, the plan path as `output_path`, `tracked_artifact: true`, and `return_to_caller: true`. |
| `superpowers:subagent-driven-development` | Execute | Pass `workflow_owner: smolpowers:smol-activate`, the exact plan path, and `return_to_caller: true`. |
| `superpowers:executing-plans` | Execute and Finish | Pass the exact plan path. This upstream owner continues into upstream branch finishing instead of returning to Smolpowers. |
| `superpowers:finishing-a-development-branch` | Finish | Pass both artifact paths and the authorized Git disposition. |

Use this handoff when the upstream skill is configured as the phase object's
owner or the user explicitly requests it for the current run. An explicit
request overrides the configured owner.

After a returning upstream owner completes, continue with the next configured
phase when the request authorizes it. Do not invoke the replaced default phase
before or after its upstream owner.

`superpowers:test-driven-development` is an Execute companion, not a phase
owner. Place it in `phases.execute.companions` and retain Smol Execute as the
explicit owner. Invoke companions first so its red-green-refactor instructions
govern implementation; the owner still reconciles plan tasks and transitions
the lifecycle.

Only substitute an upstream skill that is installed. Enabling both complete
bootstrap plugins simultaneously is not supported because both inject
lifecycle owners at session start.

## Harness tools

| Action | Claude | Codex | Kimi | Pi |
|---|---|---|---|---|
| Invoke skill | `Skill` | native skill invocation | `Skill` | native skill discovery or `/skill:name` |
| Ask a material question | `AskUserQuestion` when available | request-user-input tool when available | `AskUserQuestion` | ask in the session |
| Track tasks | task list tool when available | plan tool | `TodoList` | optional task tool or plan checkboxes |
| Delegate | `Task` | collaboration agent tools | `Agent` | optional subagent extension |
| Search/read/edit/run | native tools | native tools | `Grep`, `Glob`, `Read`, `Edit`, `Bash` | lowercase native coding tools |

Map capabilities, not literal tool names. If delegation is unavailable, execute directly.
