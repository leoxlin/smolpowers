# Test-Driven Development

Use the section matching the validated `phases.execute.tdd` configuration value. In either mode, test real behavior,
avoid mocks unless a dependency cannot be used directly, implement the minimum change, and mark a task complete only
after its outcome and specified checks pass.

## Proportional Mode

For each production behavior change:

1. Write or identify the smallest check that would fail without the change.
2. Run it and confirm the failure is caused by the missing behavior when a new automated test is practical.
3. Implement the minimum production change.
4. Run the task's exact check and relevant neighboring checks.

Do not invent a unit test for configuration, documentation, generated output, or harness metadata that does not alter
production behavior. Use the narrowest direct validator and record why.

## Strict Mode

For every production behavior change:

**NO PRODUCTION CODE WITHOUT AN OBSERVED FAILING TEST FIRST.**

### Red: Write One Failing Test

Write the smallest automated test for one behavior. Give it a clear name and name the production change that would make
it pass.

Run the focused test and inspect its output. It must fail because the behavior is missing:

- If it errors, fix the test setup and rerun it.
- If it passes immediately, revise it to exercise the missing behavior.
- Do not implement while the reason for failure is unclear.

### Green: Make It Pass

Implement only the production change required by the failing test. Do not add untested options, abstractions, or adjacent behavior.

Run the focused test and relevant neighboring checks. Fix production code rather than weakening the test. Continue only
when they pass without unexpected errors or warnings.

### Refactor: Stay Green

Only after green, remove duplication or improve names when that makes the changed code clearer. Do not add behavior
during refactoring. Rerun the focused test after every refactor, then repeat the cycle for the next behavior.

If production code was written during the current task before its test failed, remove that edit and restart at Red.
Preserve pre-existing user work; when it prevents an honest red state, report that evidence instead of claiming TDD or
discarding the work.
