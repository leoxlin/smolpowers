Use the injected `smol-activate` skill to complete the configured lifecycle.
The Plan owner is the injected `writing-plans` skill, and the Execute companion
is the injected `test-driven-development` skill.

Use the artifact slug `mixed-superpowers`. Make the existing
`tests/test_greeting.py` pass with the minimum change to `greeting.py`, then
continue automatically through Finish. Preserve the existing test, installed
skills, and configuration.

During Finish, run `python /opt/verify_finished.py`. Do not repeat its sentinel
in your final response. Do not ask questions, commit, or push. In your final
response, name each configured upstream skill you actually invoked.
