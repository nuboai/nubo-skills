# Architecture Guard Steps

Operational guide for step 1 of `nb-review-arch`. Full extension contract:
`.specify/extensions/architecture-guard/commands/architecture-review.md`.

## Delegate command

`/speckit.architecture-guard.architecture-review`

## Mode

Read-only analysis. Do not modify source files. Output findings and non-blocking refactor tasks.

## Inputs

- Feature spec: `specs/{NNN}-{feature}/spec.md`
- Plan and tasks: `specs/{NNN}-{feature}/plan.md`, `tasks.md`
- Constitutions: `.specify/memory/constitution.md`, `.specify/memory/architecture_constitution.md`
- Changed implementation files (when reviewing in-flight work)

## Outputs to capture

- Constitution drift findings with file/line evidence
- Boundary and dependency violations
- Non-blocking refactor task suggestions

## Merge into `arch-review.md`

Add a **Drift detection** section. Normalize each finding to:
`severity`, `category`, `message`, `location`, `evidence`, `recommendation`.
