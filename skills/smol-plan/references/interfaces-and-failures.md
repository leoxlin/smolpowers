# Interfaces and Failures

## Define a boundary

For each component, state:

- Who owns creation and cleanup.
- Exact inputs and outputs.
- Persisted or externally visible formats.
- Synchronous or asynchronous behavior.
- Idempotency and retry expectations.
- Errors that propagate versus errors with a real recovery path.

Keep one lifecycle owner. Do not put cleanup responsibility in both a caller and callee.

## Task boundaries

- Split tasks only when each produces an independently testable outcome or when two tasks can be reviewed independently.
- Keep scaffolding, docs, and configuration in the outcome that needs them. 
- Name cross-task interfaces in both the producing and consuming tasks. 
- Repeat exact signatures. Never rely on “as in Task N.”
