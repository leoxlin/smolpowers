# Planning Bugs and Verification

## Reproduce before choosing

1. Capture the exact command, input, environment, and observed output.
2. Confirm the behavior is repeatable.
3. Trace the bad value or state backward through callers and boundaries.
4. Compare with a working sibling path.
5. State one evidence-backed root cause.

If reproduction depends on unavailable authentication, hardware, service access, or a missing harness, record that exact gap. Do not convert a guess into the design.

## Choose verification

Prefer the narrowest check that fails for the reported defect and passes for the intended behavior. Add broader checks for affected boundaries, then retain the repository's normal suite as regression evidence.

For configuration or documentation, use schema, parser, lint, or command-output validation instead of contrived unit tests.
