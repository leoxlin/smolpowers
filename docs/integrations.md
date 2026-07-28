# Integrations

With selected upstream Superpowers skills installed, configure one by name or
request it for a single run to replace its Smolpowers phase:

- `superpowers:brainstorming` replaces Design.
- `superpowers:writing-plans` replaces Plan.
- `superpowers:subagent-driven-development` replaces Execute.
- `superpowers:finishing-a-development-branch` replaces Finish.

To use the exact upstream TDD skill instead of built-in strict mode, add it as
an Execute companion while retaining Smol Execute as the phase owner:

```json
{
  "phases": {
    "execute": {
      "owner": "smolpowers:smol-execute",
      "companions": [
        "superpowers:test-driven-development"
      ]
    }
  }
}
```

Smolpowers passes the configured artifact paths and asks returning upstream
owners to hand control back to its lifecycle. Upstream `executing-plans`
replaces both Execute and Finish because it continues directly into upstream
branch finishing.

Do not enable both plugins' session-start bootstraps together. Make only the
selected upstream skills discoverable alongside the Smolpowers bootstrap.
[PLEASE VERIFY] this installation shape in your target harness.
