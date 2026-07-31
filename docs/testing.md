# Testing

Run the full locked Python 3.14 pytest suite:

```bash
mise run test:unit
```

Pass test paths to the same wrapper for focused runs:

```bash
mise run test:unit -- tests/test_config.py
```

## Authenticated lifecycle evaluations

Run model-backed evaluations separately with
[Harbor](https://www.harborframework.com/):

```bash
PYTHONPATH=harbor \
CODEX_FORCE_AUTH_JSON=1 \
uv run --locked harbor jobs start --config harbor/config.yaml
```

The configuration runs one lifecycle task with these Codex agents:

- `codex-sp` uses the Superpowers lifecycle.
- `codex-smol` uses the Smolpowers lifecycle.
- `codex-mix` uses Smolpowers with the Superpowers plan and TDD skills.

Harbor can run up to eight trials at the same time. The three configured agents
run at the same time for the current task.

### Subscription credentials

The agents use the Codex subscription. Run `codex login` before the evaluation
so that `~/.codex/auth.json` exists. Set `CODEX_FORCE_AUTH_JSON=1` so Harbor
uses this file.

## Job dashboard and traces

Serve job outputs under `harbor/jobs` with:

```bash
uv run --locked python harbor/harbor_dashboard.py
```

The dashboard at http://127.0.0.1:8642/ re-scans on every refresh and lists
jobs, lifecycle evaluation checks, phases, and token usage per trial. A trial
passes only when `skills_in_order` and `requested_change_completed` both equal
`1` and Harbor reports no exception.
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
