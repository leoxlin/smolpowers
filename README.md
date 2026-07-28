# smolpowers

<div align="center">
  <img src="smolpowers.png" alt="A small hamster wearing a superhero cape" width="250">
  <br>
  A lightweight, evidence-driven workflow for coding agents.
</div>

## Why smolpowers

Smolpowers keeps the smallest useful loop from
[Superpowers](https://github.com/obra/superpowers), adapted from v6.2.0:

**Plan → Design → Execute → Finish**

It preserves reviewable specs, executable plans, proportional testing, and
fresh verification—without telemetry, runtime dependencies, mandatory
worktrees, or mandatory subagents.

## How it works

- `smol-activate` resumes the earliest incomplete phase.
- `smol-plan` defines the goal and writes a product spec.
- `smol-design` turns the spec into an executable implementation plan.
- `smol-execute` implements and verifies each task.
- `smol-finish` checks the requirements, complete diff, and fresh test results.

By default, specs and plans are written under `docs/superpowers/`.

## Install

Install this repository as a plugin with your coding agent's plugin manager.

For example, in Claude Code:

```text
/plugin marketplace add /absolute/path/to/smolpowers
/plugin install smolpowers@smolpowers
```

## Use

Ask your agent to use Smolpowers for a change:

```text
Use Smolpowers to add account deletion.
```

Smolpowers will start at the first phase that is not already complete and
continue through the lifecycle. You can also request a specific phase or resume
an existing spec and plan.

## Configure

Add `.smolpowers.json` to the repository root to change the artifact locations:

```json
{
  "docsRoot": "docs/superpowers",
  "stateRoot": ".superpowers"
}
```

Both values may be absolute or repository-root-relative. Missing or invalid
configuration falls back to these defaults.

## Verify

```bash
bash tests/run-all.sh
```

Integration smoke-test coverage and known gaps are recorded in [docs/integration-smoke.md](docs/integration-smoke.md).

## License

[MIT](LICENSE)
