---
name: nb-test
description: "Browser and webapp testing for the implementation."
metadata:
  phase: test
  strategy: merge
  tier: green
  composes:
    - browser-testing-with-devtools
    - webapp-testing
  nubo_version: "1.0.0"
---

# nb-test

## Purpose

Execute browser and webapp tests to verify the implementation works correctly.

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

Follow each sub-procedure below and combine outputs into the command artifacts.

1. [Browser Testing With Devtools](references/browser-testing-with-devtools.md)
2. [Webapp Testing](references/webapp-testing.md)


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Test results | `specs/{NNN}-{feature}/test-results.md` | Browser and webapp test outcomes |


## Pipeline

**Next command:** `/nb-analyze`

- Use only this successor — do not invent, skip, or substitute pipeline steps in summaries or feature artifacts.

