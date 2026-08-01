# Lifecycle Selection

## Artifacts

- **Design Spec**: `<specDir>/specs/YYYY-MM-DD-<slug>-design.md`. It records the goal, scope,
  constraints, and the chosen approach for the change.
- **Implementation Plan**: `<specDir>/plans/YYYY-MM-DD-<slug>.md`. It turns the current Design Spec into
  tasks that have commands which can verify each outcome.

## Phases

Smolpowers moves a change through four phases in a fixed order.

- **Design**: Write or update the Design Spec.
- **Plan**: Write or update the Implementation Plan.
- **Execute**: Do the tasks in the Implementation Plan.
- **Finish**: Verify the change and do the approved Git actions.

Do not skip, reorder, or run phases in parallel. Stop when Finish completes.

## Artifact State

- **Incomplete**: The artifact has placeholders, unresolved decisions, or missing required headings.
- **Stale Design Spec**: The current request or repository behavior contradicts its goal, scope, constraints, or approach.
- **Stale Implementation Plan**: It no longer implements the current Design Spec, names changed files or interfaces, or lacks commands that
  verify its outcomes.

Judge freshness by content and repository evidence, not timestamps.

## Resume Rules

- Existing Design Spec, no Implementation Plan: Plan.
- Existing Implementation Plan with unchecked tasks: Execute.
- Existing Implementation Plan with checked tasks but failing checks: Execute.
- Existing Implementation Plan with checked tasks and passing checks: Finish.
- Completed Finish phase: Complete.
- Changed request that invalidates scope: Design.
- Changed implementation shape with unchanged product decision: Plan.

If several artifact pairs exist, follow the explicitly named pair. Otherwise connect the request to artifact content before using dates as a tie-breaker.
