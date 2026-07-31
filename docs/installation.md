# Installation

Smolpowers uses the [skills CLI](https://github.com/vercel-labs/skills).
Install all five skills as one suite.

## Global installation

Use global installation by default:

```bash
npx skills add leoxlin/smolpowers --global --skill '*'
```

## Project installation

Omit `--global` to install the suite in the current project:

```bash
npx skills add leoxlin/smolpowers --skill '*'
```

## Local checkout

Use an absolute checkout path during local development:

```bash
npx skills add /absolute/path/to/smolpowers --global --skill '*'
```

Omit `--global` if you want a project installation.

After installation, start a new agent session if necessary. Request the
`smol-activate` skill by name and describe the task. Install the complete
suite because `smol-activate` contains resources that all phases use.

Installation of one phase without the complete suite is not supported.
