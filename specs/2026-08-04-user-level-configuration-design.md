# User-Level Configuration Design Spec

**Date:** 2026-08-04
**Status:** Current

## Goal

Let a user set Smolpowers configuration values that apply across repositories.

## Success

- The loader reads `~/.smolpowers.json` when the file exists.
- Repository values have priority over user-level values.
- Environment values have priority over repository and user-level values.
- Omitted values come from lower-priority configuration or the defaults.
- Invalid configuration warns once and causes one atomic fallback to all defaults.
- Unit tests verify the merge priority and failure behavior.

## Scope

### In scope

- Load configuration from the user home directory.
- Merge default, user-level, repository, and environment values in a defined order.
- Document the user-level file and the merge order.

### Out of scope

- Add a new configuration schema or configuration properties.
- Add platform-specific configuration directories.
- Add a command that writes configuration files.

## Current Context

The loader reads only `.smolpowers.json` in the repository root. It merges repository values over defaults and merges
environment values over repository values. A user must repeat shared values in each repository or use environment
variables.

## Constraints

- Keep configuration parsing, path resolution, defaults, and merge behavior in `load-config.py`.
- Preserve the current repository file path and environment variable behavior.
- Warn one time and use all defaults if one configuration file is invalid or cannot be read.
- Do not add a dependency.
- Support Python 3.10 or later.

## Considered Approaches

### Chosen: Layer the user file below the repository file

Read `~/.smolpowers.json` and merge it between defaults and repository configuration. This approach gives shared values
to each repository and keeps local control for repository-specific values.

### Rejected: Give the user file priority over the repository file

This order prevents a repository from selecting the settings that its workflow requires.

### Rejected: Use a platform configuration directory

Issue 4 specifies `~/.smolpowers.json`. A second path adds behavior that the issue does not request.

## Product Design

The loader resolves the user file with `Path.home() / ".smolpowers.json"`. It reads the user file and the repository
file when they exist. It merges values in this order, from highest priority to lowest priority: environment,
repository, user, and defaults. The existing recursive merge behavior applies at each layer.

The loader treats both files as one configuration input. If either file has invalid JSON or cannot be read, the loader
prints the existing warning one time and returns all defaults. It does not keep values from another file or from the
environment after this failure.

The configuration document describes both file locations and the complete priority order. Existing repositories that
do not have a user-level file keep their current behavior.

## Verification Strategy

Focused unit tests use an isolated home directory. They verify a user-only file, partial nested merges, repository
priority, environment priority, absent files, and invalid user-level configuration. The full unit suite verifies that
the change does not alter other configuration or skill behavior.

## Assumptions

- The user controls the home directory and its `.smolpowers.json` file.
- `Path.home()` identifies the home directory for the current process.
