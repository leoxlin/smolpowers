# Configuration

Add `.smolpowers.json` to the repository root to change artifact locations,
phase owners, ordered companions, or phase-specific settings:

```json
{
  "activation": "full",
  "specDir": "docs/superpowers",
  "stateDir": ".superpowers",
  "phases": {
    "design": {
      "owner": "brainstorming"
    },
    "execute": {
      "owner": "smol-execute",
      "companions": [],
      "tdd": "strict"
    },
    "finish": {
      "owner": "finishing-a-development-branch"
    }
  }
}
```

## Activation

- `lite`: only explicit requests to use or resume Smolpowers.
- `full` (default): new features, large refactors, and other non-trivial changes.
- `ultra`: every requested code change.

## Phases

Paths may be absolute or repository-root-relative. Each phase has one explicit
`owner` and an optional ordered `companions` array. Omitted phases and
properties use their defaults. Execute accepts `tdd: proportional` (the
default) or `strict`.

Use bare skill names. The loader also accepts a namespaced `namespace:skill`
value and keeps the namespace.

Missing or invalid configuration warns once and falls back atomically to all
defaults.

The released flat `design`, `plan`, `execute`, `finish`, and `tdd` keys remain
accepted as legacy input when `phases` is absent. Do not mix the two shapes.
