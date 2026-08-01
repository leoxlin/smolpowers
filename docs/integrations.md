# Integrations

## Superpowers

Install Superpowers with the skills CLI:

```bash
npx skills add obra/superpowers
```

With selected Superpowers skills installed, use [configuration](configuration.md) to configure which skills Smolpowers
activates in each phase.

- `brainstorming` replaces `smol-design`.
- `writing-plans` replaces `smol-plan`.
- `subagent-driven-development` replaces `smol-execute`.
- `finishing-a-development-branch` replaces `smol-finish`.

Smolpowers activates each configured skill in order. The final skill runs the phase and returns control to the
lifecycle. Upstream `executing-plans` replaces both Execute and Finish because it continues into upstream branch
finishing.

### Examples

Use the Superpowers TDD skill instead of the built-in TDD in `smol-execute`

```json
{
  "phases": {
    "execute": {
      "skills": [
        "test-driven-development",
        "smol-execute"
      ]
    }
  }
}
```

Use Superpowers for planning instead of `smol-plan`

```json
{
  "phases": {
    "plan": {
      "skills": [
        "writing-plans",
      ]
    }
  }
}
```

## OpenSpec

> Coming Soon!
