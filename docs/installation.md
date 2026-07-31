# Installation

Smolpowers uses the [skills CLI](https://github.com/vercel-labs/skills).
Install all five skills as one suite.

```bash
npx skills add leoxlin/smolpowers
```

After installation, start a new agent session. Request the `smol-activate`
skill by name and describe the task:

```text
Use the smol-activate skill to [describe the task].
```

Install the complete suite because `smol-activate` contains resources that all
phases use. Installation of one phase without the complete suite is not
supported.

## Automatic Activation (Optional)

You can add a project instruction that tells your agent to activate Smolpowers
for software changes.

For most agents, add this instruction to `AGENTS.md`:

```text
For software changes, use the smol-activate skill.
```

For Claude, add the same instruction to `CLAUDE.md`.
