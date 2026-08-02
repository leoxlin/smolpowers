# Configuration

Add `.smolpowers.json` to the repository root to change artifact locations,
ordered phase skills, or phase-specific settings:

```json
{
  "activation": "manual",
  "designDir": "docs/superpowers/specs",
  "planDir": "docs/superpowers/plans",
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

- `manual` (used when unset): only explicit requests to start or resume Smolpowers.
- `default`: matching active changes, interface decisions, high-risk behavior changes, and coordinated refactors.
- `always`: every repository change except an explicit opt-out or a read-only request.

At `default`, Smolpowers does not activate for documentation-only, test-only, formatting-only, lint-only, Git-only,
mechanical, or small known corrections. High-risk behavior affects a published interface, persisted data, configuration
schema, security, concurrency, resource lifecycle, destructive behavior, or an external effect. If no activation rule
matches, the agent uses its normal process.

The skill reads this value only after the host discovers the skill. To apply `always` to each change, add a project
instruction or a host start hook that evaluates Smol Activate for every request.

## Phases

Artifact paths can be absolute or repository-root-relative. Each phase has one ordered `skills` array. Smol Activate activates
each skill from first to last. The final skill runs the phase. Omitted phases and properties use their defaults. Execute
accepts `tdd: proportional` by default or `strict`.

Use bare skill names. The loader also accepts a namespaced `namespace:skill` value and keeps the namespace. Missing or
invalid configuration warns once and falls back atomically to all defaults.

## Environment variables

Environment variables have priority over `.smolpowers.json`. File values have priority over defaults.

| Environment variable | Configuration value |
| --- | --- |
| `SMOL_DESIGN_DIR` | `designDir` |
| `SMOL_PLAN_DIR` | `planDir` |
| `SMOL_ACTIVATION` | `activation` |
| `SMOL_PHASES_DESIGN_SKILLS` | `phases.design.skills` |
| `SMOL_PHASES_PLAN_SKILLS` | `phases.plan.skills` |
| `SMOL_PHASES_EXECUTE_SKILLS` | `phases.execute.skills` |
| `SMOL_PHASES_EXECUTE_TDD` | `phases.execute.tdd` |
| `SMOL_PHASES_FINISH_SKILLS` | `phases.finish.skills` |

Set a skill-list variable to a comma-separated list. The loader keeps the list order. For example:

```bash
SMOL_PHASES_EXECUTE_SKILLS=test-driven-development,smol-execute
```
