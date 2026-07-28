# Integration Smoke Record

**Date:** 2026-07-28

## Deterministic checks

- `bash tests/run-all.sh`: passed.
- Skill validator: all five skills passed.
- Shell syntax and ShellCheck: passed.
- Actual upstream task parser: parsed the Smolpowers plan template from the adjacent Superpowers checkout.
- Upstream substitution contracts: `brainstorming`, `writing-plans`, and `subagent-driven-development` expose return-to-caller handoffs.
- Selected upstream discovery: installed the actual `writing-plans` and `test-driven-development` skill directories beside Smolpowers in an isolated Codex home and verified their exact names in Codex's model-visible prompt.
- Plugin-creator validator: rejected only the Codex manifest's inline `"hooks": {}` field. The current Codex plugin contract accepts inline hook objects, and Smolpowers requires the empty object to suppress Claude hook auto-discovery. This validator is behind the current contract. [PLEASE VERIFY]

## Harness sessions

| Harness | Version | Local load path | Result |
|---|---:|---|---|
| Claude Code | 2.1.204 | `--plugin-dir <repo>` | Blocked: OAuth access token expired (`401`). No model response was claimed. |
| Codex | 0.145.0 | temporary `.agents/skills` discovery, `codex exec --ephemeral` | Passed: loaded the bootstrap skill, ran the loader, selected the Design phase. |
| Codex mixed lifecycle | 0.145.0 | isolated local marketplaces with selected upstream plugin skills | Passed: Smol Design, upstream Plan, upstream TDD companion, Smol Execute, and Smol Finish completed; the immutable Finish verifier passed. |
| Kimi Code | 0.29.0 | `--skills-dir <repo>/skills` | Passed: ran the loader and selected the Design phase. |
| Pi | 0.81.1 | `-e <repo> --no-session` | Passed: loaded the package bootstrap and selected the Design phase. |

The Codex and Kimi sessions exercised native skill discovery without persistently installing the repository marketplace. Their marketplace and manifest shapes are covered by the deterministic manifest tests.

## Fresh-agent scenarios

- Tiny feature: invalid configuration warned once, both default roots were used, the artifact pair was written, and two CLI tests passed.
- Bug fix: reproduced repeated hyphens, recorded the root cause and artifact pair, then passed the focused and full tests.
- Existing plan: resumed at Execute, kept two tiny independent tasks inline, completed focused tests, and stopped at Finish when an unrelated environment gate failed.
- Failing Finish: reported `RELEASE_CHANNEL` as unset and did not rewrite or hide the failing check.
- Explicit upstream handoff: selected upstream `superpowers:writing-plans` as the Plan owner, wrote only the configured `notes/plans/...` artifact, and did not run Smolpowers Plan or implementation.
- Mixed lifecycle: installed actual upstream `writing-plans` and `test-driven-development` skills beside Smolpowers, produced the upstream plan format, observed the missing-file RED failure, passed GREEN, and completed the immutable Finish verifier through `tests/test-superpowers-integration.sh`.

Forward-test fixtures were created under ignored `.superpowers/` state and removed on exit.
