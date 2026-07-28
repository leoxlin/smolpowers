# Lifecycle Selection

## Artifact states

Treat an artifact as incomplete when it has placeholders, unresolved decisions, missing required headings, or an outcome that cannot be verified.

Treat a spec as stale when the active request or relevant repository behavior materially contradicts its goal, scope, constraints, or chosen approach.

Treat a plan as stale when it no longer implements the current spec, names interfaces or files that materially changed, or lacks commands that can verify its outcomes. Do not use timestamps alone; content and repository evidence decide freshness.

## Resume rules

- Existing spec, no plan: Plan.
- Existing plan with unchecked tasks: Execute.
- Existing plan with checked tasks but failing checks: Execute.
- Existing plan with checked tasks and unverified diff: Finish.
- Changed request that invalidates scope: Design.
- Changed implementation shape with unchanged product decision: Plan.

If several artifact pairs exist, follow the explicitly named pair. Otherwise connect the request to artifact content before using dates as a tie-breaker.
