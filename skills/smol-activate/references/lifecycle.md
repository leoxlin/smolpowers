# Lifecycle Selection

## Artifacts

- **Design**: `<specDir>/specs/YYYY-MM-DD-<slug>-design.md`. The specification. It records the goal, scope,
  constraints, and the chosen approach for the change.
- **Plan**: `<specDir>/plans/YYYY-MM-DD-<slug>.md`. The implementation plan. It turns the current specification into
  tasks that have commands which can verify each outcome.

## Phases

Smolpowers moves a change through four phases in a fixed order.

- **Design**: Write or update the Design artifact.
- **Plan**: Write or update the Plan artifact.
- **Execute**: Do the tasks in the Plan artifact.
- **Finish**: Verify the change and do the approved Git actions.

Do not skip, reorder, or run phases in parallel. Stop when Finish completes.

## Artifact State

- **Incomplete**: The artifact has placeholders, unresolved decisions, or missing required headings.
- **Stale design**: The current request or repository behavior contradicts its goal, scope, constraints, or approach.
- **Stale plan**: It no longer implements the current spec, names changed files or interfaces, or lacks commands that
  verify its outcomes.

Judge freshness by content and repository evidence, not timestamps.

## Resume Rules

- Existing spec, no plan: Plan.
- Existing plan with unchecked tasks: Execute.
- Existing plan with checked tasks but failing checks: Execute.
- Existing plan with checked tasks and unverified diff: Finish.
- Existing plan with checked tasks and verified diff: Complete.
- Changed request that invalidates scope: Design.
- Changed implementation shape with unchanged product decision: Plan.

If several artifact pairs exist, follow the explicitly named pair. Otherwise connect the request to artifact content before using dates as a tie-breaker.
