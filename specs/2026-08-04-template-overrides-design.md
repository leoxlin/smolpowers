# Template Overrides Design Spec

**Date:** 2026-08-04
**Status:** Current

## Goal

Let a user select the Design Spec template and the Implementation Plan template.

## Success

- The `specTemplate` setting selects the Design Spec template.
- The `planTemplate` setting selects the Implementation Plan template.
- Each setting accepts an absolute path or a repository-root-relative path.
- An omitted setting keeps the applicable built-in template.
- Unit tests verify the normalized configuration values.

## Scope

### In scope

- Add optional `specTemplate` and `planTemplate` configuration values.
- Add environment variables for both values.
- Make the design and plan skills use the selected templates.
- Document the settings and their path rules.

### Out of scope

- Change the required headings or fields in an artifact.
- Add a template language or template interpolation.
- Add template discovery or multiple templates for one phase.

## Current Context

The design skill always uses its `references/spec-template.md` file. The plan skill always uses its
`references/plan-template.md` file. A user cannot select a repository template. The configuration loader already owns
configuration defaults, file priority, and environment overrides.

## Constraints

- Keep configuration defaults and environment mappings in `load-config.py`.
- Preserve the current configuration priority and atomic fallback.
- Preserve the built-in templates as the default behavior.
- Keep the primary headings and required plan elements from the selected template.
- Do not add a dependency or a template language.
- Support Python 3.10 or later.
- Write documentation in ASD-STE100 Simplified Technical English.

## Considered Approaches

### Chosen: Add two optional template paths

Add one path for each artifact type. The skills use a configured path or their built-in reference. This approach uses
the current configuration flow and does not add a new component.

### Rejected: Copy custom templates over built-in files

This approach changes installed skill files. It also cannot give different repositories different templates safely.

### Rejected: Add a template directory

A directory would require fixed file names and more path rules. The issue requests overrides for two known files.

## Product Design

The normalized configuration contains `specTemplate` and `planTemplate`. Their default value is `null`. The
`SMOL_SPEC_TEMPLATE` and `SMOL_PLAN_TEMPLATE` environment variables set the same values at the highest current priority.

The design skill uses `specTemplate` when it contains a path. The plan skill uses `planTemplate` when it contains a
path. A relative path starts at the repository root. An absolute path stays absolute. If a value is `null`, each skill
uses its current built-in reference.

The selected template changes artifact structure only. The design skill still requires the primary Design Spec
headings. The plan skill still requires its current status, task, interface, and verification elements. A missing or
unreadable selected template stops the applicable phase because the phase cannot make the requested artifact safely.

## Verification Strategy

Focused configuration tests verify defaults, file values, and environment priority for both settings. The full unit
suite verifies that other configuration and skill contracts do not change. Skill instructions define the observable
path selection and failure behavior. A model-backed Harbor test is not part of this change because no current Harbor
task tests custom configuration input.

## Assumptions

- The configuration property names use the current camel case convention.
- A custom template is a Markdown file that supplies the required artifact structure.
