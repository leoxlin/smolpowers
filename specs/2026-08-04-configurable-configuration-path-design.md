# Configurable Configuration Path Design Spec

**Date:** 2026-08-04
**Status:** Current

## Goal

Let a user select the repository configuration file with `SMOL_CONFIG_PATH`.

## Success

- The loader reads the file at `SMOL_CONFIG_PATH` when the variable is set.
- The loader reads `.smolpowers.json` in the repository root when the variable is not set.
- The selected file has the same priority and failure behavior as the repository file has now.
- Unit tests verify the selected path and the default path.

## Scope

### In scope

- Add `SMOL_CONFIG_PATH` as the path of the repository configuration file.
- Document the variable and its effect on configuration priority.

### Out of scope

- Change the location of the user configuration file.
- Load the selected file and the repository file at the same time.
- Add path search rules or platform-specific configuration directories.

## Current Context

The loader always reads the repository configuration from `.smolpowers.json` in the repository root. A user cannot use
a configuration file at a different path. The loader also reads `~/.smolpowers.json` as a lower-priority user file.

## Constraints

- Keep configuration parsing, path resolution, defaults, and merge behavior in `load-config.py`.
- Preserve the user configuration file and the current configuration priority.
- Preserve the current atomic fallback when the selected file cannot be read or parsed.
- Do not add a dependency.
- Support Python 3.10 or later.

## Considered Approaches

### Chosen: Replace the repository file path

Use `SMOL_CONFIG_PATH` as the complete file path when the variable is set. Otherwise, use the current repository file.
This approach adds one path choice and keeps the current merge behavior.

### Rejected: Add a third configuration file

This approach would load both the selected file and the repository file. It would require a new priority rule that the
issue does not request.

### Rejected: Treat the variable as a directory

The variable name and the issue specify a configuration path. A directory value would add an implicit file name.

## Product Design

The loader reads `SMOL_CONFIG_PATH` before it selects the repository configuration file. It uses the variable value as
a file path. If the variable is absent, it uses `<repository-root>/.smolpowers.json`. The selected file replaces the
repository file in the current merge order. The user file remains below it, and configuration value variables remain
above it.

The loader treats a missing selected file in the same way as a missing repository file. If the selected file exists but
the loader cannot read or parse it, the loader prints the current warning one time and returns all defaults.

The configuration document lists `SMOL_CONFIG_PATH` separately from configuration value variables. It explains that
the variable selects a file and does not set a value in the normalized configuration.

## Verification Strategy

Focused unit tests create a configuration file outside the repository root. They verify that `SMOL_CONFIG_PATH` selects
that file and that the loader does not also read the repository file. Existing tests verify the default repository path,
the merge priority, and the atomic fallback. The full unit suite verifies that other behavior does not change.

## Assumptions

- `SMOL_CONFIG_PATH` contains a complete file path.
- A relative `SMOL_CONFIG_PATH` uses the process working directory, as other Python file paths do.
