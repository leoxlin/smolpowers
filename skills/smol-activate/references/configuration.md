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

The `design`, `plan`, `execute`, and `finish` values name each phase owner. Invoke
the configured value instead of the default Smolpowers skill whenever routing
to that phase. Pass the repository root, configured roots, active request, and
exact artifact paths available at that point. If a configured skill is not
installed, report it instead of silently running the default owner.

Configuration is loaded when the absolute repository root, both roots, and all
four phase owners are known.
