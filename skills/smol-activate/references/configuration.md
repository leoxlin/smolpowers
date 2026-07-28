# Repository Configuration

Resolve the repository root:

```bash
git rev-parse --show-toplevel
```

Locate `scripts/load-config.sh` under the installed `smol-activate` skill and run:

```bash
bash /absolute/path/to/smol-activate/scripts/load-config.sh /absolute/repo/root
```

Parse its JSON output directly. Never use `eval`. Treat `docsRoot` as the artifact root and `stateRoot` as information only. Core Smolpowers never writes `stateRoot`.

Configuration is loaded when the absolute repository root, `docsRoot`, and `stateRoot` are known.
