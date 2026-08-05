# Configuration

Add `.smolpowers.json` to your home directory to share settings across repositories. Add the same file to a repository
root for repository-specific settings. Both files can change artifact locations, ordered phase skills, or phase-specific
settings:

```json
{
  "activation": "manual",
  "designDir": "docs/superpowers/specs",
  "planDir": "docs/superpowers/plans",
  "specTemplate": null,
  "planTemplate": null,
  "phases": {
    "design": {
      "skills": ["brainstorming"]
    },
    "execute": {
      "skills": ["test-driven-development", "smol-execute"],
      "tdd": "strict"
    },
    "finish": {
      "skills": ["smol-finish"],
      "commit": "commit the verified change",
      "push": "push the current branch"
    }
  }
}
```

## Activation

- `manual` (used when unset): only explicit requests to start or resume Smolpowers.
- `important`: matching active changes, interface decisions, high-risk behavior changes, and coordinated refactors.
- `always`: every repository change except an explicit opt-out or a read-only request.

At `important`, Smolpowers does not activate for documentation-only, test-only, formatting-only, lint-only, Git-only,
mechanical, or small known corrections. High-risk behavior affects a published interface, persisted data, configuration
schema, security, concurrency, resource lifecycle, destructive behavior, or an external effect. If no activation rule
matches, the agent uses its normal process.

The skill reads this value only after the host discovers the skill. To apply `always` to each change, add a project
instruction or a host start hook that evaluates Smol Activate for every request.

## Phases

Artifact paths can be absolute or repository-root-relative. Each phase has one ordered `skills` array. Smol Activate
activates each skill from first to last. The final skill runs the phase. Omitted phases and properties use their
defaults. Execute accepts `tdd: proportional` by default or `strict`.

`specTemplate` selects the Design Spec template. `planTemplate` selects the Implementation Plan template. Set either
value to an absolute path or a repository-root-relative path. The default `null` value uses the applicable built-in
template. A configured file that does not exist or cannot be read stops that phase.

Finish accepts `commit` and `push` instruction strings. Both properties are absent by default. A non-null value approves
only its named Git action. Smol Finish performs Git operations only after successful verification. Direct Git
instructions in the user prompt replace all configured Git operations for that run. Smol Finish commits before it pushes
and does not push if the commit fails.

Use bare skill names. The loader also accepts a namespaced `namespace:skill` value and keeps the namespace. Missing or
invalid configuration warns once and falls back atomically to all defaults.

## Environment variables

Set `SMOL_CONFIG_PATH` to select a different repository configuration file. The value is a file path. A relative path
starts from the process working directory. If the variable is not set, Smolpowers uses `.smolpowers.json` in the
repository root. The selected file replaces the repository file. It does not replace the user file.

Configuration uses this priority, from highest to lowest:

1. Environment variables
2. The selected repository configuration file
3. The user `~/.smolpowers.json` file
4. Defaults

A value in a higher-priority source replaces the same value in a lower-priority source. Other values continue to merge.

| Environment variable | Configuration value |
| --- | --- |
| `SMOL_DESIGN_DIR` | `designDir` |
| `SMOL_PLAN_DIR` | `planDir` |
| `SMOL_SPEC_TEMPLATE` | `specTemplate` |
| `SMOL_PLAN_TEMPLATE` | `planTemplate` |
| `SMOL_ACTIVATION` | `activation` |
| `SMOL_PHASES_DESIGN_SKILLS` | `phases.design.skills` |
| `SMOL_PHASES_PLAN_SKILLS` | `phases.plan.skills` |
| `SMOL_PHASES_EXECUTE_SKILLS` | `phases.execute.skills` |
| `SMOL_PHASES_EXECUTE_TDD` | `phases.execute.tdd` |
| `SMOL_PHASES_FINISH_SKILLS` | `phases.finish.skills` |
| `SMOL_PHASES_FINISH_COMMIT` | `phases.finish.commit` |
| `SMOL_PHASES_FINISH_PUSH` | `phases.finish.push` |

Set a skill-list variable to a comma-separated list. The loader keeps the list order. For example:

```bash
SMOL_PHASES_EXECUTE_SKILLS=test-driven-development,smol-execute
```
