# Integration Smoke Record

**Date:** 2026-07-28

## Deterministic suite

`bash tests/run-all.sh` runs the locked Python 3.14 pytest project. It covers:

- skill, manifest, artifact, configuration-loader, and hook contracts;
- shell syntax and ShellCheck;
- the Pi extension's Node behavior tests;
- Harbor runner input validation and both Harbor task structures;
- adjacent upstream substitution checks when a Superpowers checkout is present.

Fresh migration verification: `49 passed` with no warnings. Both Harbor
environment Dockerfiles also built successfully on `linux/amd64`.

## Harbor lifecycle cases

- `override`: injects Smolpowers and four recorder-owner skills, then verifies
  configured roots, exact phase order, current artifacts, completed plan, and
  the absence of default roots.
- `superpowers`: injects Smolpowers plus upstream `writing-plans` and
  `test-driven-development`, then verifies the observed failing test, minimum
  implementation, upstream plan shape, completed artifacts, and in-session
  Finish verification.

Each case uses a clean non-root Git fixture in a Python 3.14 container. A
root-owned Python verifier writes Harbor's reward, and Harbor stores job
artifacts under ignored `tests/jobs/`.

## Authenticated runs

The migration does not claim a model-backed result without an explicit
`AGENT=MODEL` selection and the corresponding provider credentials. Run:

```bash
uv run --project tests --locked python tests/run_harbor.py \
  --case override \
  --case superpowers \
  --agent codex=PROVIDER/MODEL
```

Repeat `--agent` to compare supported agents in the same case.
