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

`mise run test:integration` runs both configurations in sequence.

Each configuration runs one lifecycle task with three agents:

- `-sp` uses the Superpowers lifecycle.
- `-smol` uses the Smolpowers lifecycle.
- `-mix` uses Smolpowers with the Superpowers plan and TDD skills.

`harbor/config.codex.yaml` defines the Codex agents and
`harbor/config.kimi.yaml` defines the Kimi Code agents.

These are the only current model-backed harness configurations. Claude Code,
Gemini CLI, Pi, and Cursor use the same common Agent Skills files, but this
repository does not claim model-backed lifecycle evidence for them.

Run both authenticated evaluations after each skill behavior change. An older
trace does not prove the current skill revision. Before a cross-harness release,
cover these cases:

- A complete Design → Plan → Execute → Finish change
- A direct phase request that must return to activation
- A new session that reads a completed Implementation Plan
- A failed Finish check that must return to Execute

Harbor can run up to eight trials at the same time. The three configured agents
run at the same time for the current task.

### Subscription credentials

The Codex agents use the Codex subscription. Run `codex login` before the
evaluation so that `~/.codex/auth.json` exists. Set `CODEX_FORCE_AUTH_JSON=1`
so Harbor uses this file. The mise tasks set this variable for the Codex
configuration.

The Kimi Code agents use the Kimi Code subscription. Create an API key in the
Kimi Code Console and set `KIMI_API_KEY` before the evaluation. The agent
sends the key to `https://api.kimi.com/coding/v1` as `KIMI_MODEL_API_KEY` and
sets a 256K context limit.

The Kimi Code agents run the Kimi Code CLI (npm package
`@moonshot-ai/kimi-code`), not the `kimi-cli` Python package. The `-sp` agent
installs Superpowers as a managed plugin. The plugin manifest adds the skills,
starts the `using-superpowers` skill at session start, and adds the Kimi Code
tool mapping (`skillInstructions`) from `.kimi-plugin/plugin.json`. The
`-smol` and `-mix` agents get plain skills with the `--skills-dir` flag.

## Job dashboard and traces

Serve job outputs under `harbor/jobs` with:

```bash
uv run --locked python harbor/harbor_dashboard.py
```

The dashboard at http://127.0.0.1:8642/ re-scans on every refresh and lists
jobs, lifecycle evaluation checks, phases, and token usage per trial. A trial
passes only when `skills_in_order` and `requested_change_completed` both equal
`1` and Harbor reports no exception. The `-sp` agents skip the lifecycle check:
their trials report `skills_in_order` as `1` when the agent name has no entry
in `EXPECTED_SKILLS`.
Trials link to a trace
explorer at `/trace/<job>/<trial>` that renders the trial's ATIF trajectory
(`agent/trajectory.json`): every message, tool call with arguments and
observations, and skill usage, filterable by source, tool, skill, and text.

Token totals are input plus output. Cached input and reasoning tokens are shown
as subsets of input and output respectively and are not added again.

Codex trials run with `model_reasoning_summary=detailed`, so their
trajectories also include the agent's reasoning per step, shown in the trace
explorer. Trajectories written before that flag was set have no reasoning
content.
