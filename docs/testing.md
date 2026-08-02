# Testing

Run the full locked Python 3.14 pytest suite:

```bash
mise run test:unit
```

Pass test paths to the same wrapper for focused runs:

```bash
mise run test:unit -- tests/test_config.py
```

The deterministic suite validates these interfaces:

- Agent Skills names, descriptions, directory names, and metadata limits
- Local links from skill Markdown files
- OpenAI skill metadata and activation-first phase prompts
- Configuration defaults, validation, and path safety
- Skill and metadata token limits

Run `mise run lint` for Python lint and type checks. Run `mise run tokens` for
the complete skill token report.

## Authenticated lifecycle evaluations

Run model-backed evaluations separately with
[Harbor](https://www.harborframework.com/):

```bash
mise run test:integration:codex
mise run test:integration:kimi
```

`mise run test:integration` runs both model configurations in sequence.

Each configuration runs two tasks with three agents:

- `verify-small-change` verifies the complete lifecycle through one repository change.
- `verify-activation` verifies structured activation decisions.

The agents are:

- `-superpowers` uses the Superpowers lifecycle.
- `-smol` uses the Smolpowers lifecycle.
- `-mix` uses Smolpowers with the Superpowers plan and TDD skills.

`harbor/config.codex.yaml` defines the Codex agents and
`harbor/config.kimi.yaml` defines the Kimi Code agents. Each file lists both tasks under `harbor/tasks`.

The Mise commands use Harbor overrides with these selections:

- `verify-small-change` runs `-superpowers`, `-smol`, and `-mix`.
- `verify-activation` runs only `-smol`.

`verify-activation` uses `activation: important`. It checks explicit activation, explicit opt-out, analysis-only,
documentation-only, test-only, Git-only, mechanical, configuration-schema, and interface-refactor requests. The agent
writes one Boolean decision for each case. The verifier rejects missing, extra, duplicate, or incorrect decisions. The
supported commands run this task only for the `-smol` agent.

These are the only current model-backed harness configurations. Claude Code, Gemini CLI, Pi, and Cursor use the same
common Agent Skills files, but this repository does not claim model-backed lifecycle evidence for them.

Run both authenticated evaluations after each skill behavior change. An older trace does not prove the current skill
revision. Before a cross-harness release, cover these cases:

- A complete Design → Plan → Execute → Finish change
- A direct phase request that must return to activation
- A new session that reads a completed Implementation Plan
- A failed Finish check that must return to Execute
- An `important` activation matrix with both accepted and rejected requests

Harbor can run up to eight trials at the same time. The three configured agents run at the same time for each task.

### Subscription credentials

The Codex agents use the Codex subscription. Run `codex login` before the evaluation so that `~/.codex/auth.json`
exists. Set `CODEX_FORCE_AUTH_JSON=1` so Harbor uses this file. The mise tasks set this variable for the Codex
configuration.

The Kimi Code agents use the Kimi Code subscription. Create an API key in the Kimi Code Console and set `KIMI_API_KEY`
before the evaluation. The agent sends the key to `https://api.kimi.com/coding/v1` as `KIMI_MODEL_API_KEY` and sets a
256K context limit.

The Kimi Code agents run the Kimi Code CLI (npm package `@moonshot-ai/kimi-code`), not the `kimi-cli` Python package.
The `-superpowers` agent installs Superpowers as a managed plugin. The plugin manifest adds the skills, starts the
`using-superpowers` skill at session start, and adds the Kimi Code tool mapping (`skillInstructions`) from
`.kimi-plugin/plugin.json`. The `-smol` and `-mix` agents get plain skills with the `--skills-dir` flag.

## Job dashboard and traces

Serve job outputs under `harbor/jobs` with:

```bash
uv run --locked python harbor/harbor_dashboard.py
```

Token totals are input plus output. Cached input and reasoning tokens are shown as subsets of input and output
respectively and are not added again. Codex trials run with `model_reasoning_summary=detailed`, so their trajectories
also include the agent's reasoning per step, shown in the trace explorer. Trajectories written before that flag was set
have no reasoning content.
