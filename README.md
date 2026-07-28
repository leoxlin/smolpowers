# smolpowers

<div align="center">
  <img src="smolpowers.png" alt="A small hamster wearing a superhero cape" width="250">
  <br>
  A lightweight, evidence-driven workflow for coding agents.
  <br>
  <strong><a href="skills/smol-design/SKILL.md">Design</a> → <a href="skills/smol-plan/SKILL.md">Plan</a> → <a href="skills/smol-execute/SKILL.md">Execute</a> → <a href="skills/smol-finish/SKILL.md">Finish</a></strong>
</div>

## Why smolpowers

Smolpowers keeps the smallest useful loop from
[Superpowers](https://github.com/obra/superpowers), adapted from v6.2.0:

It preserves reviewable specs, executable plans, proportional testing, and
fresh verification—without telemetry, runtime dependencies, mandatory
worktrees, or mandatory subagents.

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

## Substitute upstream phases

With selected upstream Superpowers skills installed, request one by name to
replace its Smolpowers phase:

- `superpowers:brainstorming` replaces Design.
- `superpowers:writing-plans` replaces Plan.
- `superpowers:subagent-driven-development` replaces Execute.
- `superpowers:finishing-a-development-branch` replaces Finish.

Smolpowers passes the configured artifact paths and asks returning upstream
owners to hand control back to its lifecycle. Upstream `executing-plans`
replaces both Execute and Finish because it continues directly into upstream
branch finishing.

Do not enable both plugins' session-start bootstraps together. Make only the
selected upstream skills discoverable alongside the Smolpowers bootstrap.
[PLEASE VERIFY] this installation shape in your target harness.

## Verify

```bash
bash tests/run-all.sh
```

Integration smoke-test coverage and known gaps are recorded in [docs/integration-smoke.md](docs/integration-smoke.md).

## License

[MIT](LICENSE)
