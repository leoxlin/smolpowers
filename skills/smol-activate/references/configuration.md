# Repository Configuration

Resolve the repository root:

```bash
git rev-parse --show-toplevel
```

Requires Python 3.11 or later. Locate `scripts/load-config.py` under the
installed `smol-activate` skill and run:

```bash
python3 /absolute/path/to/smol-activate/scripts/load-config.py /absolute/repo/root
```

Load the complete JSON output as the configuration object. Never use `eval` or
read `.smolpowers.json` directly. The loader applies validation, defaults, path
resolution, and legacy normalization.

Use `specDir` as the artifact directory. Treat `stateDir` as information only.
Core Smolpowers never writes `stateDir`. Apply `activation` before you select a
phase.

When routing to a phase, confirm that its owner and every companion are
installed. Invoke companions in declared order through the harness's native
skill mechanism, then invoke the owner with the repository root, configured
roots, active request, and exact artifact paths available at that point. If any
skill is not installed, report that exact skill. Do not omit it or use a
default.

Use `phases.execute.tdd` for the Execute test mode.
