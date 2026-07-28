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
  --case override \
  --case superpowers \
  --agent codex=PROVIDER/MODEL
```

Repeat `--agent AGENT=MODEL` to evaluate multiple agents concurrently within
each case. Supported agents are `claude-code`, `codex`, `kimi-cli`, and `pi`.
Set the provider credentials required by the selected model.

The Superpowers case reads its checkout from `--superpowers-root`,
`SUPERPOWERS_ROOT`, or the sibling `../superpowers` directory, in that order.
