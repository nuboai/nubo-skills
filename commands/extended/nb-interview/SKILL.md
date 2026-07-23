---
name: nb-interview
description: "Stakeholder interview and idea refinement before specification."
metadata:
  phase: specify
  strategy: merge
  tier: green
  composes:
    - interview-me
    - idea-refine
  nubo_version: "1.0.0"
---

# nb-interview

## Purpose

Conduct multi-round stakeholder interviews and refine the idea before formal specification.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Pipeline routing belongs only in each command's `## Pipeline` section — never write `Next command` or `proceed to` in feature artifacts.

## User Prompts

### Prompt: scope-confirmation
- **When:** After interview rounds complete
- **Question:** "Is this scope complete?"
- **Options:**
  - `complete` -- Finalize scope and proceed to constitution/specify
  - `continue` -- Run another interview round
  - `revise` -- Revise scope summary before continuing
- **Default:** `complete`
- **Blocks:** Scope finalization



## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

Follow each sub-procedure below and combine outputs into the command artifacts.

1. [Interview Me](references/interview-me.md)
2. [Idea Refine](references/idea-refine.md)


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Interview notes | `specs/{NNN}-{feature}/interview.md` | Stakeholder input and refined scope |


## Pipeline

**Next command:** `/nb-specify`

- Use only this successor — do not invent, skip, or substitute pipeline steps in summaries or feature artifacts.

