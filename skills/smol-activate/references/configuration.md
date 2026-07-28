# Repository Configuration

Resolve the repository root:

```bash
git rev-parse --show-toplevel
```

Requires `pipx`. Locate `scripts/load-config.py` under the installed
`smol-activate` skill and run:

```bash
pipx run /absolute/path/to/smol-activate/scripts/load-config.py /absolute/repo/root
```

Parse its JSON output directly. Never use `eval`. Treat `docsRoot` as the
artifact root and `stateRoot` as information only. Core Smolpowers never writes
`stateRoot`. Apply the normalized `activation` level before selecting a phase.

The loader always returns one normalized phase object for each lifecycle phase:

```json
{
  "activation": "full",
  "phases": {
    "execute": {
      "owner": "smolpowers:smol-execute",
      "companions": [],
      "tdd": "proportional"
    }
  }
}
```

Every `phases.<name>.owner` is the sole lifecycle owner.
`phases.<name>.companions` is an ordered array of skills whose instructions
govern the owner without owning artifacts or transitions.
`phases.execute.tdd` is either `proportional` or `strict`.
`activation` is `lite`, `full`, or `ultra`.

When routing to a phase, confirm that its owner and every companion are
installed. Invoke companions in declared order through the harness's native
skill mechanism, then invoke the owner with the repository root, configured
roots, active request, and exact artifact paths available at that point. If any
skill is not installed, report that exact skill instead of dropping it or
running a default.

The preferred `.smolpowers.json` input groups settings beneath `phases`.
Released flat phase keys, ordered phase arrays, and top-level `tdd` remain
accepted as legacy input when `phases` is absent. The loader normalizes both
input shapes, so lifecycle skills consume only explicit phase objects.

Configuration is loaded when the absolute repository root, both roots,
activation level, and all four normalized phase objects are known.
