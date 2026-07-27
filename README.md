# Smolpowers

Smolpowers is a small adaptation of Superpowers v6.2.0. It keeps one lifecycle—Plan → Design → Execute → Finish—and five skills:

- `using-smolpowers`
- `plan`
- `design`
- `execute`
- `finish`

It targets Claude Code, Codex, Kimi Code, and Pi without telemetry, runtime dependencies, mandatory worktrees, mandatory subagents, or vendored heavyweight skills.

## Install

### Claude Code

Add this checkout as a local marketplace, then install the plugin:

```text
/plugin marketplace add /absolute/path/to/smolpowers
/plugin install smolpowers@smolpowers-dev
```

Claude loads the compact SessionStart bootstrap from `hooks/hooks.json`.

### Codex

Add this repository as a local marketplace, open `/plugins`, and install `smolpowers`:

```bash
codex plugin marketplace add /absolute/path/to/smolpowers
```

Codex discovers `skills/` natively. The manifest deliberately declares `"hooks": {}` so Codex does not auto-load the Claude hook.

### Kimi Code

Install this repository as a plugin:

```text
/plugins install /absolute/path/to/smolpowers
```

Kimi loads `using-smolpowers` through `sessionStart.skill` and uses the native mappings in `.kimi-plugin/plugin.json`.

### Pi

Install the checkout as a Pi package:

```bash
pi install git:github.com/OWNER/smolpowers
```

For local development:

```bash
pi -e /absolute/path/to/smolpowers
```

Replace `OWNER` with the eventual repository owner. [PLEASE VERIFY]

## Configure

Smolpowers reads only `.smolpowers.json` at the repository root:

```json
{
  "docsRoot": "docs/superpowers",
  "stateRoot": ".superpowers"
}
```

Values may be absolute or repository-root-relative. Missing configuration silently uses the defaults. Invalid configuration warns once and atomically falls back to both defaults. External paths remain subject to normal filesystem approval.

`.superpowers/` is ignored by default. Core Smolpowers does not write it.

The 2,400-word `SKILL.md` limit is a conservative proxy for provider-specific 4,000-token limits; exact equivalence depends on content and tokenizer. [PLEASE VERIFY]

Unmodified upstream subagent-driven development writes `.superpowers` directly. A custom `stateRoot` does not redirect that upstream skill without modifying upstream.

## Upstream handoff

Explicit upstream skills own their phase. For example:

- “Use `superpowers:writing-plans`; save the plan to `/repo/notes/plans/2026-07-27-cache.md`.”
- “Use `superpowers:executing-plans` for `/repo/notes/plans/2026-07-27-cache.md`.”

Smolpowers passes custom artifact paths to the upstream skill and does not create duplicate artifacts. Partial installation of selected upstream skills is supported; enabling both complete bootstrap plugins together is not guaranteed. [PLEASE VERIFY]

## Verify

```bash
bash tests/run-all.sh
```

Integration smoke tests require each harness executable and its normal authentication.

See [docs/integration-smoke.md](docs/integration-smoke.md) for the latest recorded local coverage and gaps.
