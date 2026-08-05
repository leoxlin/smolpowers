# Finish Git Operations Design Spec

**Date:** 2026-08-04
**Status:** Current

## Goal

Let a repository configure the commit and push actions that Smol Finish performs.

## Success

- The normalized configuration keeps each configured `phases.finish.commit` and `phases.finish.push` value.
- Both properties are absent by default, and Smol Finish does not perform either Git action.
- A non-null value gives Smol Finish instructions and approval for only that Git action.
- Unit tests verify configuration behavior and structural skill contracts. Harbor tests verify skill behavior.

## Scope

### In scope

- Add optional commit and push settings to the finish phase.
- Make Smol Finish follow each configured instruction after successful verification.
- Document the settings and their environment variable overrides.

### Out of scope

- Add new Git commands, dependencies, or a Git wrapper.
- Open or merge pull requests from the new settings.
- Change the existing verification requirements.

## Current Context

The configuration loader keeps unknown user keys. However, it does not supply commit or push defaults or environment
overrides. Smol Finish performs only a Git action that the current user request approves. It does not treat repository
configuration as prior approval.

## Constraints

- Keep all configuration defaults, parsing, and environment mappings in `load-config.py`.
- A local commit must not give approval to push.
- Smol Finish must complete verification before it performs any Git action.
- Commit subjects must use the repository conventional commit format.
- The change must not add a dependency.

## Considered Approaches

### Chosen: Optional instruction settings

Support `commit` and `push` in the finish configuration. Use an absent property as the disabled value. Treat each string
as the instructions and prior approval for its named action. This approach reuses the current configuration loader and
the agent Git tools.

### Rejected: Boolean settings

A Boolean value cannot carry the instructions requested in [issue 3](https://github.com/leoxlin/smolpowers/issues/3).

### Rejected: A Git command runner

A new runner duplicates the host Git tools and adds a second lifecycle owner.

## Product Design

The loader does not add the properties to the finish defaults. It maps `SMOL_PHASES_FINISH_COMMIT` and
`SMOL_PHASES_FINISH_PUSH` to these settings. File settings and environment settings use the current merge priority.

After final verification, Smol Finish examines the two settings. For each non-null setting, it follows the instruction
and performs only that action. If the user prompt gives Git instructions, Smol Finish ignores all configured Git
operations and follows the prompt. For both sources, it commits before it pushes. A commit failure prevents a push. A
push failure does not change the verified implementation result.

## Verification Strategy

Unit tests verify absent defaults, file merge behavior, environment overrides, override priority, skill size, and links.
Harbor tests verify skill behavior.

## Assumptions

- A non-null commit or push value is a string with instructions for that action.
- Repository owners control `.smolpowers.json` and its environment overrides.
