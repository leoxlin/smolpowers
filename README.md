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

<br>
<div align="center">
  <table align="center">
    <thead>
      <tr>
        <th>Category</th>
        <th>🐹 <em>Smolpowers</em></th>
        <th>🦸 <strong>Superpowers</strong></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td align="center">Features</td>
        <td align="center">Minimal</td>
        <td align="center">Robust</td>
      </tr>
      <tr>
        <td align="center">Coverage</td>
        <td align="center">SDD only</td>
        <td align="center">Full SDLC</td>
      </tr>
      <tr>
        <td align="center">Customization</td>
        <td align="center">Configurable</td>
        <td align="center">Opinionated and fixed</td>
      </tr>
      <tr>
        <td align="center">Composability</td>
        <td align="center">Modular and composable</td>
        <td align="center">Complete framework</td>
      </tr>
    </tbody>
  </table>
</div>
<br>

Smolpowers does not aim to replace Superpowers or replicate its effectiveness. Instead, it provides a simpler SDD loop
with the same reviewable specifications, executable plans, proportional testing, and post-execution verification. You
can also [compose](docs/integrations.md) Superpowers skills with Smolpowers whenever you need additional rigor or
functionality.

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

Report bugs and request features in [Discussions](https://github.com/leoxlin/smolpowers/discussions).

## License

[MIT](LICENSE)
