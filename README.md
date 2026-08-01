# smolpowers

<div align="center">
  <img src="smolpowers.png" alt="A small hamster wearing a superhero cape" width="250">
  <br>
  A lightweight, evidence-driven workflow for coding agents.
  <br>
  <strong><a href="skills/smol-design/SKILL.md">Design</a> → <a href="skills/smol-plan/SKILL.md">Plan</a> → <a href="skills/smol-execute/SKILL.md">Execute</a> → <a href="skills/smol-finish/SKILL.md">Finish</a></strong>
</div>

## Why smolpowers

Smolpowers is a lightweight SDD framework based on [Superpowers](https://github.com/obra/superpowers).

It does not aim to replace Superpowers or replicate its effectiveness. Instead, it provides a simpler SDD loop with the
same reviewable specifications, executable plans, proportional testing, and post-execution verification. You can also
[compose](docs/integrations.md) Superpowers skills with Smolpowers whenever you need additional rigor or functionality.

| Category      | 🐹 *Smolpowers*        | 🦸 **Superpowers**                 |
|---------------|------------------------|------------------------------------|
| Features      | Minimal                | Robust                             |
| Coverage      | SDD only               | Full SDLC                          |
| Customization | Configurable           | Opinionated and fixed              |
| Composability | Modular and composable | Complete framework                 |

Use Smolpowers when composability, configurability, and easy integration with other skills matter more than a complete
development framework.

## Quickstart

Install Smolpowers:

```bash
npx skills add leoxlin/smolpowers --skill '*'
```

Then invoke the activation skill:

```text
/smol-activate [describe the task].
```

## Documentation

- [Installation](docs/installation.md) — installation and optional automatic activation.
- [Configuration](docs/configuration.md) — schema, defaults, and examples.
- [Integrations](docs/integrations.md) — using selected upstream Superpowers skills.
- [Testing](docs/testing.md) — deterministic tests and model-backed evaluations.

## License

[MIT](LICENSE)
