---
name: nb-review-skill
description: "Review nubo-skills command definitions for governance compliance."
metadata:
  phase: review
  strategy: standalone
  tier: amber
  composes:
    - nubo-review-skill
  nubo_version: "1.0.0"
---

# nb-review-skill

## Purpose

Review skill/command definitions in nubo-skills for governance, naming, and completion contract compliance.

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

Review nubo-skills command definitions for structural and governance compliance.

1. Load `registry.yml` and compare each registered command to its on-disk `SKILL.md`.
2. Verify naming (`nb-{command}`), layer path, strategy, and `composes` alignment.
3. Check required sections for the command's strategy and output mode.
4. Confirm artifact paths follow `specs/{NNN}-{feature}/` conventions.
5. Record findings by severity in `specs/{NNN}-{feature}/skill-review.md`.


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Skill review | `specs/{NNN}-{feature}/skill-review.md` | Governance review findings |


## Pipeline

**Terminal command** — no pipeline successor.


