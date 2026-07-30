# Testing

Run the full locked Python 3.14 pytest suite:

```bash
bash tests/run-all.sh
```

Pass test paths to the same wrapper for focused runs:

```bash
bash tests/run-all.sh tests/test_config.py
```

The deterministic suite includes Harbor task validation without making model
requests.

## Authenticated lifecycle evaluations

Run model-backed evaluations separately with
[Harbor](https://www.harborframework.com/):

```bash
uv run --project tests --locked python tests/run_harbor.py \
  --case base \
  --case override \
  --case superpowers \
  --agent codex=openai/gpt-5.6-sol
```

Repeat `--agent AGENT=MODEL` to evaluate multiple agents concurrently within
each case. Supported agents are `claude-code`, `codex`, `kimi-cli`, and `pi`.
Set the provider credentials required by the selected model.

### Subscription credentials

The runner wires host subscription logins automatically for the selected
agents; variables already present in the environment take precedence.

- `codex` and `pi` use the Codex (ChatGPT) subscription. Codex reads
  `~/.codex/auth.json` (`CODEX_FORCE_AUTH_JSON=1`); Pi injects
  `~/.pi/agent/auth.json` into the trial container. Models must use the
  `openai/…` and `openai-codex/…` providers respectively.
- `kimi-cli` and `claude-code` use the Kimi subscription. The OAuth token in
  `~/.kimi-code/credentials/kimi-code.json` is exported as `KIMI_API_KEY` for
  kimi-cli (`kimi/…` models) and as `ANTHROPIC_AUTH_TOKEN` with
  `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/anthropic` for claude-code.

```bash
uv run --project tests --locked python tests/run_harbor.py \
  --case override \
  --agent codex=openai/gpt-5.6-sol \
  --agent pi=openai-codex/gpt-5.6-sol \
  --agent kimi-cli=kimi/kimi-for-coding \
  --agent claude-code=kimi-for-coding
```

The Superpowers case reads its checkout from `--superpowers-root`,
`SUPERPOWERS_ROOT`, or the sibling `../superpowers` directory, in that order.

## Job dashboard and traces

Serve job outputs under `tests/jobs` with:

```bash
uv run --project tests --locked python tests/harbor_dashboard.py
```

The dashboard at http://127.0.0.1:8642/ re-scans on every refresh and lists
jobs, lifecycle evaluation checks, phases, and token usage per trial. A trial
passes only when `skills_in_order` and `requested_change_completed` both equal
`1` and Harbor reports no exception. Older jobs are labeled `legacy verifier`.
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
