---
name: nb-converge
description: "Iterate on gaps until spec and implementation converge."
metadata:
  phase: converge
  strategy: wrap
  tier: green
  composes:
    - speckit-converge
  nubo_version: "1.0.0"
---

# nb-converge

## Purpose

Drive iteration cycles until the implementation converges with the specification.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Pipeline routing belongs only in each command's `## Pipeline` section — never write `Next command` or `proceed to` in feature artifacts.



## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

Iterate between implementation and analysis until spec and code converge.

1. Run gap analysis against the feature spec.
2. Identify unresolved gaps and classify by severity.
3. Generate fix tasks for P0-P1 gaps.
4. Re-implement and re-analyze until no P0-P1 gaps remain.
5. Document convergence history in `specs/{NNN}-{feature}/convergence.md`.

## Artifact rules

- `convergence.md` records **status only** (`CONVERGED` / `NOT CONVERGED`), iteration history, gates, and accepted deviations.
- Do **not** write `Next command`, `proceed to`, or pipeline routing in `convergence.md` or other feature artifacts — routing lives in each command's `## Pipeline` section.
- If a later pipeline artifact already exists (e.g. `checklist.md` is SHIP), note that status in the iteration log; do not skip ahead to a later command in summaries.


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Convergence log | `specs/{NNN}-{feature}/convergence.md` | Iteration history and resolution |


## Pipeline

**Next command:** `/nb-checklist`

- Use only this successor — do not invent, skip, or substitute pipeline steps in summaries or feature artifacts.

