# Installation

Smolpowers uses the [skills CLI](https://github.com/vercel-labs/skills). Install all five skills as one suite.

```bash
npx skills add leoxlin/smolpowers --skill '*'
```

After installation, start a new agent session. Request the `smol-activate` skill by name and describe the task:

```text
Use the smol-activate skill to [describe the task].
```

Install the complete suite because `smol-activate` contains resources that all phases use. Installation of one phase
without the complete suite is not supported.

## Runtime Requirements

Smolpowers requires Git and Python 3.10 or later. The activation skill uses the first available Python 3 command from
`python3`, `python`, or `py -3`.
