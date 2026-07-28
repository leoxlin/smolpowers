# Installation

Smolpowers supports Claude Code, Codex, Kimi Code, and Pi.

## Claude Code

```bash
claude plugin marketplace add leoxlin/smolpowers
claude plugin install smolpowers@smolpowers
```

## Codex

```bash
codex plugin marketplace add leoxlin/smolpowers
codex plugin add smolpowers@smolpowers
```

Start a new Codex session after installation.

## Kimi Code

Run Kimi Code, then enter:

```text
/plugins install https://github.com/leoxlin/smolpowers
/reload
```

Confirm that you trust the third-party source when prompted.

## Pi

```bash
pi install git:github.com/leoxlin/smolpowers
```

## Install from a local checkout

Replace the remote source above with the checkout path:

```text
Claude Code: claude plugin marketplace add /absolute/path/to/smolpowers
Codex:       codex plugin marketplace add /absolute/path/to/smolpowers
Kimi Code:   /plugins install /absolute/path/to/smolpowers
Pi:          pi install /absolute/path/to/smolpowers
```
