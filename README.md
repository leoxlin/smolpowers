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
fresh verification—without telemetry, third-party runtime packages, mandatory
worktrees, or mandatory subagents.

By default, specs and plans are written under `docs/superpowers/`.

## Quickstart

Install Smolpowers:

```bash
npx skills add leoxlin/smolpowers --skill '*'
```

Then request the activation skill by name:

```text
Use the smol-activate skill to [describe the task].
```

## Documentation

- [Installation](docs/installation.md) — installation and optional automatic activation.
- [Configuration](docs/configuration.md) — schema, defaults, and examples.
- [Integrations](docs/integrations.md) — using selected upstream Superpowers skills.
- [Testing](docs/testing.md) — deterministic tests and model-backed evaluations.

## License

[MIT](LICENSE)
