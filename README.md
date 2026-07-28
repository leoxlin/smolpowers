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

Add `.smolpowers.yml` to the repository root to change artifact locations,
phase owners, ordered companions, or phase-specific settings:

```yaml
docsRoot: docs/superpowers
stateRoot: .superpowers
phases:
  design:
    owner: superpowers:brainstorming
  execute:
    owner: smolpowers:smol-execute
    companions: []
    tdd: strict
  finish:
    owner: superpowers:finishing-a-development-branch
```

Paths may be absolute or repository-root-relative. Each phase has one explicit
`owner` and an optional ordered `companions` array. Omitted phases and
properties use their defaults. Execute accepts `tdd: proportional` (the
default) or `strict`. Missing or invalid configuration falls back atomically to
all defaults.

The released flat `design`, `plan`, `execute`, `finish`, and `tdd` keys remain
accepted as legacy input when `phases` is absent. Do not mix the two shapes.
Reading a configuration file requires
[Mike Farah `yq` v4](https://github.com/mikefarah/yq); an absent file uses
defaults without invoking `yq`.

## Substitute upstream phases

With selected upstream Superpowers skills installed, configure one by name or
request it for a single run to replace its Smolpowers phase:

- `superpowers:brainstorming` replaces Design.
- `superpowers:writing-plans` replaces Plan.
- `superpowers:subagent-driven-development` replaces Execute.
- `superpowers:finishing-a-development-branch` replaces Finish.

To use the exact upstream TDD skill instead of built-in strict mode, add it as
an Execute companion while retaining Smol Execute as the phase owner:

```yaml
phases:
  execute:
    owner: smolpowers:smol-execute
    companions:
      - superpowers:test-driven-development
```

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

Run the authenticated, model-backed integration lifecycles separately:

```bash
bash tests/test-overrides-integration.sh
bash tests/test-superpowers-integration.sh
```

The focused suite runs the selected-Superpowers installation and discovery
portion without authentication or a model request.

Integration smoke-test coverage and known gaps are recorded in [docs/integration-smoke.md](docs/integration-smoke.md).

## License

[MIT](LICENSE)
