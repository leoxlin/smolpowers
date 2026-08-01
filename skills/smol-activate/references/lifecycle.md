# Lifecycle Selection

## Artifacts

- **Design Spec**: `<designDir>/YYYY-MM-DD-<slug>-design.md`. It records the goal, scope,
  constraints, and the chosen approach for the change.
- **Implementation Plan**: `<planDir>/YYYY-MM-DD-<slug>.md`. It turns the current Design Spec into
  tasks that have commands which can verify each outcome. Its `Status` is `Active` or `Complete`.

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
- **Complete Finish**: The Implementation Plan status is `Complete`. Finish sets this value only after all required checks pass.

Judge freshness by content and repository evidence, not timestamps.

## Resume Rules

- Existing Design Spec, no Implementation Plan: Plan.
- Existing Implementation Plan with unchecked tasks: Execute.
- Existing Implementation Plan with checked tasks but failing checks: Execute and set its status to `Active`.
- Existing Implementation Plan with checked tasks, passing checks, and `Active` status: Finish.
- Existing Implementation Plan with `Complete` status: Complete.
- Changed request that invalidates scope: Design.
- Changed implementation shape with unchanged product decision: Plan.

If several artifact pairs exist, follow the explicitly named pair. Otherwise connect the request to artifact content before using dates as a tie-breaker.
