Replace the link shortener's in-memory storage with SQLite so links survive an
application restart. Use the configured `DATABASE` path, preserve the existing
API, and ensure the test suite passes.
