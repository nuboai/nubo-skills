---
name: nb-review-security
description: "Security hardening review and static analysis."
metadata:
  phase: review
  strategy: merge
  tier: green
  composes:
    - security-and-hardening
    - static-analysis
  nubo_version: "1.0.0"
  allowed_tools:
    - read_file
    - grep
  read_only: true
  globs:
    - "**/*.{ts,py,go,rs,java}"
---

# nb-review-security

## Purpose

Run security hardening review combined with static analysis for vulnerability detection.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Pipeline routing belongs only in each command's `## Pipeline` section — never write `Next command` or `proceed to` in feature artifacts.

## User Prompts

### Prompt: remediation-delegation
- **When:** Security findings are detected
- **Question:** "Create remediation tasks for these findings?"
- **Options:**
  - `create-tasks` -- Generate remediation tasks for nb-implement
  - `report-only` -- Keep findings in security report only
  - `escalate` -- Escalate critical findings for immediate action
- **Default:** `create-tasks`
- **Blocks:** Remediation task generation



## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

Follow each sub-procedure below and combine outputs into the command artifacts.

1. [Security And Hardening](references/security-and-hardening.md)
2. [Static Analysis](references/static-analysis.md)


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Security report | `specs/{NNN}-{feature}/security-review.md` | Security findings and SARIF output |


## Pipeline

**Next command:** `/nb-implement`

- Use only this successor — do not invent, skip, or substitute pipeline steps in summaries or feature artifacts.

