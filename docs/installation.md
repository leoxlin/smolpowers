# Installation

Smolpowers uses the [skills CLI](https://github.com/vercel-labs/skills).
Install all five skills as one suite.

```bash
npx skills add leoxlin/smolpowers --skill '*'
```

After installation, start a new agent session. Request the `smol-activate`
skill by name and describe the task:

```text
Use the smol-activate skill to [describe the task].
```

Install the complete suite because `smol-activate` contains resources that all
phases use. Installation of one phase without the complete suite is not
supported.

## Runtime Requirements

Smolpowers requires Git and Python 3.10 or later. The activation skill uses the
first available Python 3 command from `python3`, `python`, or `py -3`.

## Automatic Activation (Optional)

You can add a project instruction that tells your agent to activate Smolpowers
for software changes.

Add this instruction to the repository instruction file that your harness
loads:

```text
For software changes, use the smol-activate skill.
```

- Use `AGENTS.md` for Codex, Kimi Code CLI, Pi, and other harnesses that load it.
- Use `CLAUDE.md` for Claude Code.
- Use `GEMINI.md` for Gemini CLI.
- Use a Cursor project rule if your Cursor setup does not load `AGENTS.md`.
