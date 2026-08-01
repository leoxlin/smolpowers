# Configuration

Add `.smolpowers.json` to the repository root to change artifact locations,
ordered phase skills, or phase-specific settings:

```json
{
  "activation": "default",
  "specDir": "docs/superpowers",
  "stateDir": ".superpowers",
  "phases": {
    "design": {
      "skills": ["brainstorming"]
    },
    "execute": {
      "skills": ["test-driven-development", "smol-execute"],
      "tdd": "strict"
    },
    "finish": {
      "skills": ["finishing-a-development-branch"]
    }
  }
}
```

## Activation

- `manual`: only explicit requests to use or resume Smolpowers.
- `default` (used when unset): new features, large refactors, and other non-trivial changes.
- `always`: every requested code change.

## Phases

Paths can be absolute or repository-root-relative. Each phase has one ordered `skills` array. Smol Activate activates
each skill from first to last. The final skill runs the phase. Omitted phases and properties use their defaults. Execute
accepts `tdd: proportional` by default or `strict`.

Use bare skill names. The loader also accepts a namespaced `namespace:skill` value and keeps the namespace. Missing or
invalid configuration warns once and falls back atomically to all defaults.
