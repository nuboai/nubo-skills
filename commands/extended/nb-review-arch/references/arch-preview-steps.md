# Architect Preview Steps

Operational guide for step 2 of `nb-review-arch`. Full preset contract:
`.specify/presets/architect-preview/templates/commands/preview.md`.

## Delegate command

`/speckit.architect-preview`

Pass the feature scope or change summary as arguments (e.g. plan summary, affected modules).

## Mode

Read-only impact analysis. Do not modify architecture memory or source files.

## Inputs

- Current feature artifacts under `specs/{NNN}-{feature}/`
- Existing architecture memory under `.specify/memory/architecture*.md`
- Optional: diff summary or list of affected components

## Outputs to capture

- Architectural impact areas (modules, boundaries, data flows)
- Complexity and risk assessment
- Coupling, migration, or operational risks

## Merge into `arch-review.md`

Add an **Impact preview** section. Summarize blast radius, risk level, and
pre-implementation concerns before contract validation runs.
