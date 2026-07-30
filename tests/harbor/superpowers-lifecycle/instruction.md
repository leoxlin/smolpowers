Use the injected `smol-activate` skill to complete the configured lifecycle.
The Plan owner is the injected `writing-plans` skill, and the Execute companion
is the injected `test-driven-development` skill.

Use the artifact slug `mixed-superpowers`. Make the existing
test suite pass by replacing the link shortener's in-memory storage with SQLite
in `app.py`. Use the configured `DATABASE` path and preserve the existing API,
then continue automatically through Finish. Preserve the existing tests,
installed skills, and configuration.

During Finish, run `python /opt/verify_finished.py`. Do not repeat its sentinel
in your final response. Do not ask questions, commit, or push. In your final
response, name each configured upstream skill you actually invoked.
