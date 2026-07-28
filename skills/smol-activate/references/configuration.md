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

The `design`, `plan`, `execute`, and `finish` values each contain a phase chain:
either one skill-name string or a non-empty ordered array of skill-name
strings. Normalize a string to a one-item chain. The final item is the sole
phase owner; every leading item is a companion whose instructions govern the
owner's work without owning artifacts or transitions.

When routing to a phase, confirm that every skill in its phase chain is
installed. Invoke companions in declared order through the harness's native
skill mechanism, then invoke the owner with the repository root, configured
roots, active request, and exact artifact paths available at that point. If any
skill is not installed, report that exact skill instead of dropping it or
running a default.

Configuration is loaded when the absolute repository root, both roots, and all
four phase chains are known.
