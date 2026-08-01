# Integrations

Install Superpowers with the skills CLI:

```bash
npx skills add obra/superpowers
```

With selected upstream Superpowers skills installed, use
[configuration](configuration.md) to configure one as the final phase skill.
You can also request it for one run:

- `brainstorming` replaces Design.
- `writing-plans` replaces Plan.
- `subagent-driven-development` replaces Execute.
- `finishing-a-development-branch` replaces Finish.

To use the exact upstream TDD skill instead of built-in strict mode, put it
before Smol Execute:

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

Smolpowers activates each configured skill in order. The final skill runs the
phase and returns control to the lifecycle. Upstream `executing-plans`
replaces both Execute and Finish because it continues into upstream branch
finishing.

Install the selected upstream skills with the five Smolpowers skills. Then,
request `smol-activate` by name.
