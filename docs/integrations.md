# Integrations

With selected upstream Superpowers skills installed, configure one by name or
request it for a single run to replace its Smolpowers phase:

- `brainstorming` replaces Design.
- `writing-plans` replaces Plan.
- `subagent-driven-development` replaces Execute.
- `finishing-a-development-branch` replaces Finish.

To use the exact upstream TDD skill instead of built-in strict mode, add it as
an Execute companion while retaining Smol Execute as the phase owner:

```json
{
  "phases": {
    "execute": {
      "owner": "smol-execute",
      "companions": [
        "test-driven-development"
      ]
    }
  }
}
```

Smolpowers passes the configured artifact paths and asks returning upstream
owners to hand control back to its lifecycle. Upstream `executing-plans`
replaces both Execute and Finish because it continues directly into upstream
branch finishing.

Install the selected upstream skills with the five Smolpowers skills. Then,
request `smol-activate` by name.
